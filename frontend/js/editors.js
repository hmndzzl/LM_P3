import { showErrors } from './errors.js';

const $ = (id) => document.getElementById(id);
let symbols = [];
let nextId = 0;
let freeVariables = [];
const assignments = new Map();

// Las altas y bajas notifican el mismo cambio que una edición de un campo.
function notifyEdit() {
  $('workspace').dispatchEvent(new Event('input', { bubbles: true }));
}

function node(tag, text = '') {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
}

function domainValues() {
  return $('domain').value === '' ? [] : $('domain').value.split('\n');
}

function domainSelect(value, id, onChange) {
  const select = node('select');
  select.id = id;
  select.append(new Option('Elegir elemento', ''));
  for (const element of [...new Set(domainValues())]) {
    if (element !== '') select.append(new Option(element, element));
  }
  if (value && !domainValues().includes(value)) select.append(new Option(`${value} (fuera de D)`, value));
  select.value = value;
  select.addEventListener('input', () => onChange(select.value));
  return select;
}

function updateCoverage(symbol) {
  const status = $(`coverage-${symbol.id}`);
  if (symbol.kind === 'predicate') {
    status.textContent = `${symbol.rows.length} tuplas ingresadas. La relación debe contener al menos una.`;
    return;
  }
  const domain = new Set(domainValues().filter((value) => value !== ''));
  const expected = domain.size ** symbol.arity;
  if (!Number.isSafeInteger(expected)) {
    status.textContent = 'La tabla requiere demasiadas combinaciones para contarlas aquí. Reduce el dominio o la aridad.';
    return;
  }
  const defined = new Set(symbol.rows.filter((row) => row.arguments.length === symbol.arity
    && row.arguments.every((value) => domain.has(value)) && domain.has(row.output))
    .map((row) => JSON.stringify(row.arguments))).size;
  status.textContent = domain.size && Number.isInteger(symbol.arity) && symbol.arity >= 0
    ? `Salidas definidas: ${defined}. Faltan ${Math.max(0, expected - defined)} de ${expected} combinaciones. Se comprobarán conflictos al evaluar.`
    : 'Introduce un dominio y una aridad válidos para comprobar las salidas pendientes.';
}

function interpretationTable(symbol, entries) {
  const table = node('table');
  table.className = 'interpretation-table';
  table.append(node('caption', `${symbol.name || 'Sin nombre'} · ${symbol.kind === 'function' && symbol.arity === 0 ? 'constante' : `aridad ${symbol.arity ?? 'sin definir'}`}`));
  const head = node('thead');
  const headings = node('tr');
  for (const title of symbol.kind === 'function' ? ['Argumentos', 'Imagen'] : ['Tupla']) {
    const cell = node('th', title);
    cell.scope = 'col';
    headings.append(cell);
  }
  head.append(headings);
  const body = node('tbody');
  for (const entry of entries) {
    const row = node('tr');
    row.append(node('td', `(${entry.arguments.map((value) => value || 'pendiente').join(', ')})`));
    if (symbol.kind === 'function') row.append(node('td', entry.output || 'pendiente'));
    body.append(row);
  }
  table.append(head, body);
  return table;
}

function domainList(values) {
  const list = node('ul');
  list.className = 'domain-elements';
  for (const value of values) list.append(node('li', value || 'Elemento vacío'));
  return list;
}

function appendPreview(target, entries, render, unit = 'filas') {
  target.append(render(entries.slice(0, 4)));
  if (entries.length <= 4) return;
  const more = node('details');
  more.className = 'summary-more';
  more.append(node('summary', `Ver ${unit} restantes (${entries.length - 4})`));
  more.addEventListener('toggle', () => {
    if (!more.open || more.dataset.loaded) return;
    more.dataset.loaded = 'true';
    more.append(render(entries.slice(4)));
  });
  target.append(more);
}

export function updateWorldSummary() {
  const domain = domainValues();
  $('domain-overview').replaceChildren();
  if (domain.length) appendPreview($('domain-overview'), domain, domainList, 'elementos');
  else $('domain-overview').textContent = 'Dominio sin definir.';
  $('language-count').textContent = symbols.length
    ? `${symbols.length} símbolos ingresados`
    : 'Sin símbolos declarados';

  for (const [kind, target, empty] of [
    ['predicate', 'predicates-overview', 'Sin predicados declarados.'],
    ['function', 'functions-overview', 'Sin funciones ni constantes declaradas.'],
  ]) {
    $(target).replaceChildren();
    const group = symbols.filter((symbol) => symbol.kind === kind);
    if (!group.length) $(target).textContent = empty;
    for (const symbol of group) {
      const section = node('div');
      section.className = 'symbol-summary';
      appendPreview(section, symbol.rows, (rows) => interpretationTable(symbol, rows));
      if (!symbol.rows.length) section.append(node('p', 'Sin filas definidas.'));
      $(target).append(section);
    }
  }
}

function addSymbol(kind, name = '', arity = 1, rows = []) {
  symbols.push({ id: nextId++, kind, name, arity, rows });
  renderSymbols();
  renderInterpretations();
}

function renderSymbols() {
  $('symbols').replaceChildren();
  for (const symbol of symbols) {
    const row = node('tr');
    const kindCell = node('td', symbol.kind === 'function' ? 'Función' : 'Predicado');
    row.append(kindCell);
    for (const field of ['name', 'arity']) {
      const cell = node('td');
      const input = node('input');
      input.id = `symbol-${symbol.id}-${field}`;
      input.setAttribute('aria-label', `${field === 'name' ? 'Nombre' : 'Aridad'} del símbolo ${symbol.id + 1}`);
      input.type = field === 'arity' ? 'number' : 'text';
      if (field === 'arity') {
        input.min = '0';
        input.max = '32';
      }
      let previousArity = symbol.arity;
      input.value = symbol[field];
      input.addEventListener('input', () => {
        symbol[field] = field === 'arity' ? (input.value === '' ? null : Number(input.value)) : input.value;
      });
      input.addEventListener('change', () => {
        if (field === 'arity' && Number.isInteger(symbol.arity) && symbol.arity >= 0 && symbol.arity <= 32) {
          const losesValues = symbol.rows.some((entry) => entry.arguments.slice(symbol.arity).some((value) => value !== ''));
          if (losesValues && !confirm('Al reducir la aridad se borrarán los argumentos sobrantes de las filas. ¿Continuar?')) {
            symbol.arity = previousArity;
            input.value = previousArity;
            return;
          }
          for (const entry of symbol.rows) {
            entry.arguments = entry.arguments.slice(0, symbol.arity);
            while (entry.arguments.length < symbol.arity) entry.arguments.push('');
          }
          previousArity = symbol.arity;
        }
        renderInterpretations();
        notifyEdit();
      });
      cell.append(input);
      row.append(cell);
    }
    const cell = node('td');
    const remove = node('button', 'Quitar');
    remove.type = 'button';
    remove.setAttribute('aria-label', `Quitar símbolo ${symbol.id + 1}`);
    remove.addEventListener('click', () => {
      if (symbol.rows.length && !confirm('Se eliminarán este símbolo y sus filas. ¿Continuar?')) return;
      symbols = symbols.filter((item) => item !== symbol);
      renderSymbols();
      renderInterpretations();
      notifyEdit();
      $('add-predicate').focus();
    });
    cell.append(remove);
    row.append(cell);
    $('symbols').append(row);
  }
}

function renderInterpretations() {
  $('interpretations').replaceChildren();
  if (!symbols.length) $('interpretations').append(node('p', 'Declara un símbolo para introducir sus tablas.'));
  for (const symbol of symbols) {
    const section = node('section');
    section.className = 'interpretation';
    section.id = `table-${symbol.id}`;
    section.tabIndex = -1;
    section.append(node('h3', `${symbol.name || 'Sin nombre'} · ${symbol.kind === 'function' ? 'función' : 'predicado'} · aridad ${symbol.arity ?? 'pendiente'}`));
    const coverage = node('p');
    coverage.id = `coverage-${symbol.id}`;
    coverage.className = 'help';
    section.append(coverage);
    section.addEventListener('input', () => updateCoverage(symbol));
    if (!symbol.rows.length) section.append(node('p', 'No hay filas. Añade al menos una.'));
    symbol.rows.forEach((entry, index) => {
      const row = node('div');
      row.className = 'tuple-row';
      row.id = `row-${symbol.id}-${index}`;
      row.tabIndex = -1;
      entry.arguments.forEach((value, argumentIndex) => {
        const label = node('label', `Argumento ${argumentIndex + 1}`);
        const input = domainSelect(value, `tuple-${symbol.id}-${index}-${argumentIndex}`,
          (selected) => { entry.arguments[argumentIndex] = selected; });
        label.append(input);
        row.append(label);
      });
      if (!entry.arguments.length) row.append(node('span', 'Tupla vacía ()'));
      if (symbol.kind === 'function') {
        const label = node('label', 'Salida');
        const input = domainSelect(entry.output, `output-${symbol.id}-${index}`,
          (selected) => { entry.output = selected; });
        label.append(input);
        row.append(label);
      }
      const remove = node('button', 'Quitar fila');
      remove.type = 'button';
      remove.setAttribute('aria-label', `Quitar fila ${index + 1} de ${symbol.name || 'símbolo sin nombre'}`);
      remove.addEventListener('click', () => {
        symbol.rows.splice(index, 1);
        renderInterpretations();
        notifyEdit();
        $(`add-row-${symbol.id}`).focus();
      });
      row.append(remove);
      section.append(row);
    });
    const add = node('button', symbol.kind === 'function' ? 'Añadir salida' : 'Añadir tupla');
    add.id = `add-row-${symbol.id}`;
    add.type = 'button';
    add.addEventListener('click', () => {
      // No se genera D^n: el usuario introduce las filas y M2 comprueba totalidad.
      if (!Number.isInteger(symbol.arity) || symbol.arity < 0 || symbol.arity > 32 || symbol.rows.length >= 2000) {
        showErrors([{ message: 'Para este editor usa aridad de 0 a 32 y hasta 2000 filas por símbolo.', field: `language.${symbol.kind === 'function' ? 'functions' : 'predicates'}.${symbol.name}` }], errorTarget);
        return;
      }
      symbol.rows.push({ arguments: Array(symbol.arity).fill(''), output: '' });
      renderInterpretations();
      notifyEdit();
      const index = symbol.rows.length - 1;
      ($(`tuple-${symbol.id}-${index}-0`) || $(`output-${symbol.id}-${index}`) || $(`add-row-${symbol.id}`)).focus();
    });
    section.append(add);
    $('interpretations').append(section);
    updateCoverage(symbol);
  }
}

export function inputData(revision) {
  const data = { revision, functions: [], predicates: [], formula: $('formula').value,
    domain: domainValues(), function_rows: Object.create(null), relations: Object.create(null), assignments: [] };
  for (const symbol of symbols) {
    if (symbol.kind === 'function') {
      data.functions.push([symbol.name, symbol.arity]);
      data.function_rows[symbol.name] = symbol.rows.map((entry) => [entry.arguments, entry.output]);
    } else {
      data.predicates.push([symbol.name, symbol.arity]);
      data.relations[symbol.name] = symbol.rows.map((entry) => entry.arguments);
    }
  }
  data.assignments = freeVariables.filter((name) => assignments.get(name))
    .map((name) => [name, assignments.get(name)]);
  return data;
}

export function renderEnvironment(names) {
  freeVariables = names;
  $('environment').replaceChildren();
  $('environment-note').textContent = names.length
    ? `Variables libres: ${names.join(', ')}. Elige un valor de D para cada una.`
    : 'No hay variables libres; no se necesita entorno.';
  names.forEach((name, index) => {
    const label = node('label', `${name}:`);
    const select = node('select');
    select.id = `assignment-${index}`;
    const domain = [...new Set(domainValues())].filter((value) => value !== '');
    select.append(new Option(domain.length ? 'Selecciona un elemento de D' : 'Primero define el dominio D', ''));
    for (const value of domain) select.append(new Option(value, value));
    const saved = assignments.get(name);
    select.value = domain.includes(saved) ? saved : '';
    if (saved && !domain.includes(saved)) {
      const warning = node('p', `Asignación anterior ${name}: ${saved}. Ese valor ya no pertenece a D; elige otro elemento.`);
      warning.id = `assignment-warning-${index}`;
      warning.className = 'help';
      select.setAttribute('aria-describedby', warning.id);
      $('environment').append(warning);
    }
    select.addEventListener('change', () => {
      assignments.set(name, select.value);
      $(`assignment-warning-${index}`)?.remove();
      select.removeAttribute('aria-describedby');
    });
    label.append(select);
    $('environment').append(label);
  });
}

export function errorTarget(field = '', issue = {}) {
  if (field === 'formula') return $('formula');
  if (field.startsWith('environment')) {
    const sentNames = freeVariables.filter((name) => assignments.get(name));
    const name = field.startsWith('environment[') ? sentNames[Number(field.match(/\[(\d+)\]/)?.[1])] : field.slice(12);
    const index = freeVariables.indexOf(name);
    return $(`assignment-${index}`) || $('analyze');
  }
  if (field.startsWith('domain')) return $('domain');
  for (const [kind, key] of [['function', 'functions'], ['predicate', 'predicates']]) {
    const group = symbols.filter((symbol) => symbol.kind === kind);
    const prefix = `language.${key}`;
    if (field.startsWith(prefix)) {
      const index = Number(field.slice(prefix.length).match(/^\[(\d+)\]/)?.[1]);
      const symbol = Number.isInteger(index) ? group[index] : group.find((item) => field === `${prefix}.${item.name}`);
      return symbol ? $(`symbol-${symbol.id}-${issue.code === 'invalid_arity' ? 'arity' : 'name'}`) : $('add-predicate');
    }
    for (const symbol of group) {
      const tableKey = kind === 'function' ? 'functions' : 'relations';
      const prefix = `${tableKey}.${symbol.name}`;
      if (field === prefix || field.startsWith(`${prefix}[`)) {
        const suffix = field.slice(prefix.length);
        const row = suffix.match(/^\[(\d+)\]/)?.[1];
        const argument = suffix.match(/(?:\.arguments)?\[(\d+)\]$/)?.[1];
        if (row !== undefined) {
          if (suffix.endsWith('.output')) return $(`output-${symbol.id}-${row}`);
          if (argument !== undefined && suffix !== `[${row}]`) return $(`tuple-${symbol.id}-${row}-${argument}`);
          return $(`row-${symbol.id}-${row}`) || $(`table-${symbol.id}`);
        }
        return $(`table-${symbol.id}`);
      }
    }
  }
  return $('evaluate');
}

export function initializeEditors() {
  updateWorldSummary();
  $('domain').addEventListener('change', () => {
    renderInterpretations();
    renderEnvironment(freeVariables);
  });
  for (const kind of ['function', 'predicate']) {
    $(`add-${kind}`).addEventListener('click', () => {
      addSymbol(kind);
      notifyEdit();
      $(`symbol-${symbols.at(-1).id}-name`).focus();
    });
  }
}

export function clearEditors() {
  symbols = [];
  nextId = 0;
  assignments.clear();
  freeVariables = [];
  $('domain').value = '';
  $('formula').value = '';
  renderSymbols();
  renderInterpretations();
  renderEnvironment([]);
  $('environment-note').textContent = 'Se identificarán las variables libres al evaluar. También puedes revisarlas antes para elegir sus valores.';
  $('example-note').replaceChildren();
  $('example-note').hidden = true;
  $('start-description').hidden = false;
  $('language-config').open = false;
  $('interpretation-config').open = false;
  updateWorldSummary();
}

export function loadExample(example) {
  clearEditors();
  // Cada carga tiene sus propias filas: editar un ejemplo no modifica el catálogo.
  const data = structuredClone(example.data);
  $('domain').value = data.domain.join('\n');
  $('formula').value = data.formula;
  for (const [name, arity] of data.functions) {
    addSymbol('function', name, arity, data.function_rows[name].map(([args, output]) => ({ arguments: args, output })));
  }
  for (const [name, arity] of data.predicates) {
    addSymbol('predicate', name, arity, data.relations[name].map((args) => ({ arguments: args })));
  }
  for (const [name, value] of data.assignments) assignments.set(name, value);
  renderEnvironment(data.assignments.map(([name]) => name));
  $('example-note').append(node('p', example.description), node('p', example.practice));
  $('example-note').hidden = false;
  $('start-description').hidden = true;
  updateWorldSummary();
  $('result-state').textContent = 'Ejemplo cargado. Listo para evaluar.';
  $('evaluate').focus();
}
