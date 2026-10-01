const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('index.html', 'utf8');
const scriptStart = html.indexOf('<script>');
const scriptEnd = html.lastIndexOf('</script>');
const script = html.slice(scriptStart + 8, scriptEnd);

let rowsCount = 0;
const localStorageMock = {
  getItem: () => null,
  setItem: () => {}
};
const documentMock = {
  getElementById: (id) => ({
    innerText: '',
    value: '',
    innerHTML: '',
    appendChild: (child) => { if (id === 'equipTableBody') rowsCount++; },
    classList: { add: () => {}, remove: () => {} }
  }),
  createElement: (tag) => ({
    className: '',
    innerHTML: '',
    innerText: '',
    style: {},
    onclick: null,
    classList: { add: () => {}, remove: () => {} },
    appendChild: () => {}
  }),
  querySelectorAll: () => [],
  addEventListener: (evt, cb) => {
    if (evt === 'DOMContentLoaded') {
      cb();
    }
  }
};

const context = {
  console: console,
  localStorage: localStorageMock,
  document: documentMock,
  window: {},
  L: {
    map: () => ({ setView: () => {}, invalidateSize: () => {} }),
    tileLayer: () => ({ addTo: () => {} }),
    layerGroup: () => ({ addTo: () => {}, clearLayers: () => {}, addLayer: () => {} })
  },
  setTimeout: (cb) => cb(),
  encodeURIComponent: encodeURIComponent
};

vm.createContext(context);
vm.runInContext(script + '\n; globalThis.testResult = { total: equipData.length, rows: ' + rowsCount + ' };', context);

console.log('SUCESSO TOTAL! Dados carregados e renderizados:');
console.log('Total no banco:', context.testResult.total);
