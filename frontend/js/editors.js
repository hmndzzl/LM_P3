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
      if (field === 'arity') input.min = '0';
      input.value = symbol[field];
      input.addEventListener('input', () => {
        symbol[field] = field === 'arity' ? (input.value === '' ? null : Number(input.value)) : input.value;
      });
      input.addEventListener('change', renderInterpretations);
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
    if (!symbol.rows.length) section.append(node('p', 'No hay filas. Añade al menos una.'));
    symbol.rows.forEach((entry, index) => {
      const row = node('div');
      row.className = 'tuple-row';
      entry.arguments.forEach((value, argumentIndex) => {
        const label = node('label', `Argumento ${argumentIndex + 1}`);
        const input = node('input');
        input.id = `tuple-${symbol.id}-${index}-${argumentIndex}`;
        input.value = value;
        input.addEventListener('input', () => { entry.arguments[argumentIndex] = input.value; });
        label.append(input);
        row.append(label);
      });
      if (!entry.arguments.length) row.append(node('span', 'Tupla vacía ()'));
      if (symbol.kind === 'function') {
        const label = node('label', 'Salida');
        const input = node('input');
        input.id = `output-${symbol.id}-${index}`;
        input.value = entry.output;
        input.addEventListener('input', () => { entry.output = input.value; });
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
      if (!Number.isInteger(symbol.arity) || symbol.arity < 0 || symbol.arity > 32 || symbol.rows.length >= 200) {
        showErrors([{ message: 'Para este editor usa aridad de 0 a 32 y hasta 200 filas por símbolo.', field: `language.${symbol.kind === 'function' ? 'functions' : 'predicates'}.${symbol.name}` }], errorTarget);
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
    const label = node('label', name);
    const select = node('select');
    select.id = `assignment-${index}`;
    select.append(new Option('Selecciona un elemento', ''));
    for (const value of domainValues()) select.append(new Option(value, value));
    if (assignments.has(name) && !domainValues().includes(assignments.get(name))) {
      select.append(new Option(`${assignments.get(name)} (fuera de D)`, assignments.get(name)));
    }
    select.value = assignments.get(name) || '';
    select.addEventListener('change', () => assignments.set(name, select.value));
    label.append(select);
    $('environment').append(label);
  });
}

export function errorTarget(field = '') {
  if (field === 'formula') return $('formula');
  if (field.startsWith('environment')) {
    const index = field.startsWith('environment[') ? Number(field.match(/\[(\d+)\]/)?.[1]) : freeVariables.indexOf(field.slice(12));
    return $(`assignment-${index}`) || $('analyze');
  }
  if (field.startsWith('domain')) return $('domain');
  for (const [kind, key] of [['function', 'functions'], ['predicate', 'predicates']]) {
    const group = symbols.filter((symbol) => symbol.kind === kind);
    const prefix = `language.${key}`;
    if (field.startsWith(prefix)) {
      const index = Number(field.slice(prefix.length).match(/^\[(\d+)\]/)?.[1]);
      const symbol = Number.isInteger(index) ? group[index] : group.find((item) => field === `${prefix}.${item.name}`);
      return symbol ? $(`symbol-${symbol.id}-name`) : $('add-predicate');
    }
    for (const symbol of group) {
      const tableKey = kind === 'function' ? 'functions' : 'relations';
      if (field === `${tableKey}.${symbol.name}` || field.startsWith(`${tableKey}.${symbol.name}[`)) return $(`table-${symbol.id}`);
    }
  }
  return $('evaluate');
}

export function initializeEditors() {
  for (const kind of ['function', 'predicate']) {
    $(`add-${kind}`).addEventListener('click', () => {
      addSymbol(kind);
      notifyEdit();
      $(`symbol-${symbols.at(-1).id}-name`).focus();
    });
  }
}

export function loadExample() {
  symbols = [];
  assignments.clear();
  freeVariables = [];
  $('domain').value = 'norte\ncentro\nsur';
  $('formula').value = 'Activa(x)';
  addSymbol('function', 'relevo', 1, [
    { arguments: ['norte'], output: 'centro' }, { arguments: ['centro'], output: 'sur' },
    { arguments: ['sur'], output: 'norte' },
  ]);
  addSymbol('predicate', 'Activa', 1, [{ arguments: ['norte'] }, { arguments: ['centro'] }]);
  assignments.set('x', 'centro');
  renderEnvironment(['x']);
  $('environment-note').textContent = 'Variables libres: x. Ejemplo con x = centro.';
  $('example-note').hidden = false;
}
