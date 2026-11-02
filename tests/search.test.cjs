// Regression test: compact homepage has no search JS; recipe controls still work.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor() { this.hidden = true; this.attributes = {}; this.listeners = {}; }
  addEventListener(type, callback) { this.listeners[type] = callback; }
  setAttribute(key, value) { this.attributes[key] = value; }
  fire(type) { this.listeners[type]?.(); }
}
function fixture({storageFails = false, initialContrast = false, withPrint = true} = {}) {
  const contrast = new Element();
  const print = withPrint ? new Element() : null;
  const classes = {};
  let printCalls = 0;
  const written = [];
  const document = {
    documentElement: {classList: {toggle(key, enabled) { classes[key] = enabled; }}},
    querySelector(key) {
      if (key === '.contrast-toggle') return contrast;
      if (key === '.print-button') return print;
      return null;
    }
  };
  vm.runInNewContext(readFileSync('static/site.js', 'utf8'), {
    document,
    window: {print() {printCalls++;}},
    localStorage: {
      getItem() { if (storageFails) throw Error('storage disabled'); return initialContrast ? 'true' : null; },
      setItem(key, value) { if (storageFails) throw Error('storage disabled'); written.push([key, value]); }
    }
  });
  return {contrast, print, classes, written, getPrintCalls() {return printCalls;}};
}

let f = fixture({storageFails: true});
assert.equal(f.contrast.hidden, false);
assert.equal(f.classes['high-contrast'], false);
f.contrast.fire('click');
assert.equal(f.classes['high-contrast'], true);
assert.equal(f.contrast.attributes['aria-pressed'], 'true');
f.print.fire('click');
assert.equal(f.getPrintCalls(), 1);

f = fixture({initialContrast: true});
assert.equal(f.classes['high-contrast'], true);
f.contrast.fire('click');
assert.equal(f.classes['high-contrast'], false);
assert.equal(f.written.length, 1);
assert.deepEqual(f.written[0], ['recipe-high-contrast', 'false']);

f = fixture({withPrint: false});
assert.equal(f.print, null);
console.log('Recipe-page contrast, printing, blocked storage, and optional controls passed.');
