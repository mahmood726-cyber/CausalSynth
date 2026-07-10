// Headless numerical harness for CausalSynth's statistical engine.
//
// Extracts the pure (DOM-free) math functions from causal-synth.html by
// brace-matching their source, evaluates them in a vm sandbox, runs them on
// fixed inputs, and prints the results as JSON on stdout. The Python test
// tests/test_js_engine_numeric.py consumes this and independently re-derives
// the expected values, so the JS engine is verified without a browser.
//
// Usage: node tests/js_engine_harness.js
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HTML_PATH = path.join(__dirname, '..', 'causal-synth.html');
const html = fs.readFileSync(HTML_PATH, 'utf8');

// Extract a top-level `function NAME(...) { ... }` block by brace matching.
function extractFunction(src, name) {
  const decl = 'function ' + name + '(';
  const start = src.indexOf(decl);
  if (start === -1) throw new Error('function not found: ' + name);
  // find the opening brace of the body
  let i = src.indexOf('{', start);
  if (i === -1) throw new Error('no body brace for: ' + name);
  let depth = 0;
  let inStr = null;      // current string/template delimiter
  let inLineComment = false;
  let inBlockComment = false;
  for (; i < src.length; i++) {
    const c = src[i];
    const prev = src[i - 1];
    if (inLineComment) { if (c === '\n') inLineComment = false; continue; }
    if (inBlockComment) { if (c === '*' && src[i + 1] === '/') { inBlockComment = false; i++; } continue; }
    if (inStr) {
      if (c === '\\') { i++; continue; }       // skip escaped char
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === '/' && src[i + 1] === '/') { inLineComment = true; i++; continue; }
    if (c === '/' && src[i + 1] === '*') { inBlockComment = true; i++; continue; }
    if (c === '"' || c === "'" || c === '`') { inStr = c; continue; }
    if (c === '{') depth++;
    else if (c === '}') {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error('unbalanced braces for: ' + name);
}

const NAMES = [
  'lnGamma', 'normalCDF', 'normalQuantile', 'pval', 'chi2CDF',
  'tQuantile', 'regIncBeta', 'tCDF', 'tPval',
  'dlMeta', 'remlMeta', 'computeEggerTest',
];

let bundle = '';
for (const n of NAMES) bundle += extractFunction(html, n) + '\n';

const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(bundle + '\nthis.__api = {' + NAMES.join(',') + '};', sandbox);
const api = sandbox.__api;

// ---- Fixed test inputs ----
// A small heterogeneous dataset (log-OR style) for DL/REML.
// Chosen so Q > k-1 -> tau2 > 0, exercising the DL heterogeneity branch and
// the REML Fisher-scoring iteration (not the degenerate FE fallback).
const yi = [0.10, 0.80, 0.20, 0.90, -0.20];
const sei = [0.10, 0.15, 0.12, 0.14, 0.13];

// A >=10-study dataset with deliberate small-study asymmetry for Egger.
const eyi  = [0.80, 0.55, 0.40, 0.35, 0.30, 0.28, 0.25, 0.22, 0.20, 0.18, 0.15];
const esei = [0.40, 0.35, 0.30, 0.25, 0.22, 0.20, 0.18, 0.16, 0.14, 0.12, 0.10];

const out = {
  inputs: { yi, sei, eyi, esei },
  dl: api.dlMeta(yi, sei),
  dl_k1: api.dlMeta([0.42], [0.13]),
  dl_empty: api.dlMeta([], []),
  reml: api.remlMeta(yi, sei),
  egger: api.computeEggerTest(eyi, esei),
  egger_too_few: api.computeEggerTest(yi, sei),   // k=5 < 10 -> null
};

process.stdout.write(JSON.stringify(out));
