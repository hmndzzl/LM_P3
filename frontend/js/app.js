import { request } from './api.js';

const $ = (id) => document.getElementById(id);
let symbols = [];
let nextId = 0;
let revision = 0;
let busy = false;
let dirty = false;
let freeVariables = [];
const assignments = new Map();

function node(tag, text = '') {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
}

function clearErrors() {
  $('errors').hidden = true;
  $('error-list').replaceChildren();
  document.querySelectorAll('.field-error').forEach((element) => element.remove());
  document.querySelectorAll('[aria-invalid]').forEach((element) => {
    element.removeAttribute('aria-invalid');
    element.setAttribute('aria-describedby', element.dataset.description || '');
  });
}

function invalidate() {
  revision += 1;
  dirty = true;
  clearErrors();
  $('result').hidden = true;
  $('evidence').replaceChildren();
  $('empty-result').hidden = false;
  $('result-state').textContent = 'Cambiaste los datos. Vuelve a evaluar.';
  $('environment-note').textContent = 'Vuelve a analizar si cambiaste la fórmula o el lenguaje.';
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
      invalidate();
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
        invalidate();
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
        showErrors([{ message: 'Para este editor usa aridad de 0 a 32 y hasta 200 filas por símbolo.', field: `language.${symbol.kind === 'function' ? 'functions' : 'predicates'}.${symbol.name}` }]);
        return;
      }
      symbol.rows.push({ arguments: Array(symbol.arity).fill(''), output: '' });
      renderInterpretations();
      invalidate();
      const index = symbol.rows.length - 1;
      ($(`tuple-${symbol.id}-${index}-0`) || $(`output-${symbol.id}-${index}`) || $(`add-row-${symbol.id}`)).focus();
    });
    section.append(add);
    $('interpretations').append(section);
  }
}

function inputData() {
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

function renderEnvironment(names) {
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

function errorTarget(field = '') {
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

function showErrors(issues) {
  clearErrors();
  $('result').hidden = true;
  $('empty-result').hidden = false;
  $('result-state').textContent = 'No evaluado. Revisa los mensajes.';
  issues.forEach((issue, index) => {
    const target = errorTarget(issue.field);
    const item = node('li');
    const link = node('a', issue.message);
    link.href = `#${target.id}`;
    link.addEventListener('click', (event) => {
      event.preventDefault();
      target.focus();
      if (issue.span && target === $('formula')) {
        const offset = (position) => Array.from(target.value).slice(0, position).join('').length;
        target.setSelectionRange(offset(issue.span.start), offset(issue.span.end));
      }
    });
    item.append(link);
    $('error-list').append(item);
    const local = node('p', issue.message);
    local.id = `field-error-${index}`;
    local.className = 'field-error';
    if (!target.hasAttribute('aria-invalid')) target.dataset.description = target.getAttribute('aria-describedby') || '';
    target.setAttribute('aria-invalid', 'true');
    target.setAttribute('aria-describedby', `${target.getAttribute('aria-describedby') || ''} ${local.id}`.trim());
    target.insertAdjacentElement('afterend', local);
  });
  $('errors').hidden = false;
  $('errors').focus();
}

function reasonText(trace) {
  const checked = trace.checked_elements.length;
  const reasons = {
    predicate_member: 'La tupla evaluada pertenece a la relación.',
    predicate_not_member: 'La tupla evaluada no pertenece a la relación.',
    negation: 'La negación invierte el valor de su subfórmula.',
    conjunction: 'La conjunción es verdadera cuando ambos operandos son verdaderos.',
    disjunction: 'La disyunción es verdadera cuando al menos un operando es verdadero.',
    implication: 'La implicación solo es falsa con antecedente verdadero y consecuente falso.',
    biconditional: 'El bicondicional es verdadero cuando ambos operandos tienen el mismo valor.',
    existential_witness: `Testigo: ${trace.variable} = ${trace.decisive_element}.`,
    universal_counterexample: `Contraejemplo: ${trace.variable} = ${trace.decisive_element}.`,
    universal_complete: `Comprobados ${checked} de ${trace.domain_size} elementos.`,
    existential_complete: `Ningún elemento cumple la condición: comprobados ${checked} de ${trace.domain_size}.`,
  };
  return reasons[trace.reason] || 'Consulta la evidencia de las subfórmulas.';
}

function evidenceNode(trace) {
  const details = node('details');
  details.append(node('summary', `${trace.formula} — ${trace.value ? 'Verdadero' : 'Falso'}`));
  // El detalle se crea al abrirlo para no dibujar toda una traza grande de golpe.
  details.addEventListener('toggle', () => {
    if (!details.open || details.dataset.loaded) return;
    details.dataset.loaded = 'true';
    details.append(node('p', reasonText(trace)));
    details.append(node('p', trace.environment.length
      ? `Entorno: ${trace.environment.map(([name, value]) => `${name} = ${value}`).join(', ')}`
      : 'Sin asignaciones en este alcance.'));
    for (const term of trace.terms) details.append(node('p', `${term.term} = ${term.value}`));
    if (trace.unvisited_elements.length) details.append(node('p', `No visitados: ${trace.unvisited_elements.join(', ')}.`));
    for (const child of trace.children) details.append(evidenceNode(child));
  });
  return details;
}

async function run(evaluate) {
  if (busy) return;
  clearErrors();
  $('result').hidden = true;
  $('empty-result').hidden = false;
  const version = revision;
  busy = true;
  $('evaluate').disabled = true;
  $('analyze').disabled = true;
  document.querySelector('.result-panel').setAttribute('aria-busy', 'true');
  $('result-state').textContent = evaluate ? 'Evaluando…' : 'Analizando…';
  try {
    const data = inputData();
    const analysis = await request('analyze', {
      revision: version, functions: data.functions, predicates: data.predicates, formula: data.formula,
    });
    if (version !== revision || analysis.revision !== version) return;
    renderEnvironment(analysis.free_variables);
    if (!evaluate) {
      $('result-state').textContent = 'Fórmula analizada. Aún no evaluada.';
      return;
    }
    const response = await request('evaluate', inputData());
    if (version !== revision || response.revision !== version) return;
    const result = response.evaluation;
    $('result-formula').textContent = data.formula;
    $('result-value').textContent = result.value ? 'Verdadero' : 'Falso';
    $('result-value').dataset.value = String(result.value);
    $('result-reason').textContent = reasonText(result.trace);
    $('evidence').replaceChildren(evidenceNode(result.trace));
    $('empty-result').hidden = true;
    $('result').hidden = false;
    $('result-state').textContent = `Evaluación completada: ${result.value ? 'Verdadero' : 'Falso'}.`;
  } catch (error) {
    if (version === revision) showErrors(error.issues || [{ message: error.message, field: '' }]);
  } finally {
    busy = false;
    $('evaluate').disabled = false;
    $('analyze').disabled = false;
    document.querySelector('.result-panel').setAttribute('aria-busy', 'false');
  }
}

$('workspace').addEventListener('input', invalidate);
$('workspace').addEventListener('change', (event) => {
  if (event.target.tagName === 'SELECT') invalidate();
});
$('workspace').addEventListener('submit', (event) => { event.preventDefault(); run(true); });
$('analyze').addEventListener('click', () => run(false));
for (const kind of ['function', 'predicate']) {
  $(`add-${kind}`).addEventListener('click', () => {
    addSymbol(kind);
    invalidate();
    $(`symbol-${symbols.at(-1).id}-name`).focus();
  });
}
$('load-example').addEventListener('click', () => {
  if (dirty && !confirm('Se reemplazarán tus datos por el ejemplo. ¿Continuar?')) return;
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
  invalidate();
  $('environment-note').textContent = 'Variables libres: x. Ejemplo con x = centro.';
  $('example-note').hidden = false;
});
