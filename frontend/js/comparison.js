import { request } from './api.js';
import { createEvidence, reasonText } from './evidence.js';

const $ = (id) => document.getElementById(id);
let base = null;
let targets = [];
let version = 0;

function node(tag, text = '') {
  const element = document.createElement(tag);
  element.textContent = text;
  return element;
}

function valueSelect(value, id) {
  const select = node('select');
  select.id = id;
  for (const element of base.domain) select.append(new Option(element, element));
  select.value = value;
  return select;
}

function relationArguments() {
  const target = targets[Number($('comparison-target').value)];
  return Array.from({ length: target.arity }, (_, index) => $(`comparison-arg-${index}`).value);
}

function relationMember(target, args) {
  return base.relations[target.symbol].some((row) => JSON.stringify(row) === JSON.stringify(args));
}

function invalidateVariant() {
  version += 1;
  $('comparison-results').hidden = true;
  $('comparison-errors').hidden = true;
  const target = targets[Number($('comparison-target').value)];
  $('compare').disabled = !target;
  if (!target) {
    $('comparison-status').textContent = 'No hay datos disponibles para modificar.';
    return;
  }
  if (target.kind === 'relation') {
    const args = relationArguments();
    const member = relationMember(target, args);
    const tuple = `(${args.join(', ')})`;
    $('comparison-before').textContent = `${tuple} ${member ? 'pertenece' : 'no pertenece'} a ${target.symbol}.`;
    $('comparison-after').textContent = `${member ? 'Quitar' : 'Añadir'} ${tuple} ${member ? 'de' : 'a'} ${target.symbol}.`;
  } else {
    const value = $('comparison-new-value').value;
    $('comparison-before').textContent = `${target.label}`;
    $('comparison-after').textContent = `${target.symbol}${target.kind === 'function' ? `(${target.arguments.join(', ')}) →` : ':'} ${value}`;
    $('compare').disabled = value === target.before;
  }
  $('comparison-status').textContent = $('compare').disabled
    ? 'Selecciona un valor diferente al original.' : 'Cambio listo para comparar.';
}

function renderValue() {
  $('comparison-value').replaceChildren();
  const target = targets[Number($('comparison-target').value)];
  if (!target) return;
  if (target.kind !== 'relation') {
    const label = node('label', target.kind === 'function' ? 'Nueva imagen' : 'Nueva asignación');
    label.append(valueSelect(target.before, 'comparison-new-value'));
    $('comparison-value').append(label);
  } else {
    const tupleFields = node('div');
    tupleFields.className = 'tuple-row';
    for (let index = 0; index < target.arity; index += 1) {
      const label = node('label', `Componente ${index + 1} de la tupla`);
      label.append(valueSelect(base.domain[0], `comparison-arg-${index}`));
      tupleFields.append(label);
    }
    if (target.arity === 0) tupleFields.append(node('p', 'Tupla vacía ()'));
    $('comparison-value').append(tupleFields);
  }
  invalidateVariant();
}

function renderTargets() {
  targets = [
    ...base.functions.flatMap(([symbol]) => base.function_rows[symbol].map(([args, before], index) =>
      ({ kind: 'function', symbol, arguments: args, before, index, label: `${symbol}(${args.join(', ')}) → ${before}` }))),
    ...base.predicates.map(([symbol, arity]) => ({ kind: 'relation', symbol, arity, label: symbol })),
    ...base.assignments.map(([symbol, before], index) => ({ kind: 'assignment', symbol, before, index, label: `${symbol}: ${before}` })),
  ];
  $('comparison-target').replaceChildren();
  for (const [kind, title] of [['function', 'Imágenes de funciones'], ['relation', 'Relaciones'], ['assignment', 'Asignaciones libres']]) {
    const group = node('optgroup');
    group.label = title;
    targets.forEach((target, index) => {
      if (target.kind !== kind) return;
      const option = new Option(target.label, String(index));
      option.dataset.kind = kind;
      group.append(option);
    });
    if (group.children.length) $('comparison-target').append(group);
  }
  if (!targets.length) $('comparison-target').append(new Option('Sin datos disponibles', ''));
  renderValue();
}

function variantFromControls() {
  const variant = structuredClone(base);
  const target = targets[Number($('comparison-target').value)];
  if (target.kind === 'function') {
    variant.function_rows[target.symbol][target.index][1] = $('comparison-new-value').value;
  } else if (target.kind === 'assignment') {
    variant.assignments[target.index][1] = $('comparison-new-value').value;
  } else {
    const args = relationArguments();
    if (relationMember(target, args)) {
      variant.relations[target.symbol] = variant.relations[target.symbol]
        .filter((row) => JSON.stringify(row) !== JSON.stringify(args));
    } else variant.relations[target.symbol].push(args);
  }
  return variant;
}

function scenarioPanel(title, result, changedIds) {
  const section = node('section');
  section.append(node('h3', title));
  const formula = node('p', base.formula);
  formula.className = 'formula evaluated-formula';
  const value = node('p', result.value ? 'Verdadero' : 'Falso');
  value.className = 'truth';
  value.dataset.value = String(result.value);
  const selected = node('p', 'Abre un paso para resaltar su subfórmula.');
  selected.className = 'help';
  section.append(formula, value, node('p', reasonText(result.trace)), selected,
    createEvidence(result.trace, base.formula, formula, selected, changedIds));
  return section;
}

async function runComparison() {
  if (!base || !targets.length || $('compare').disabled) return;
  const current = version;
  $('compare').disabled = true;
  $('comparison-errors').hidden = true;
  $('comparison-results').hidden = true;
  $('comparison-status').textContent = 'Evaluando ambos escenarios…';
  try {
    const response = await request('compare', { revision: current, base, variant: variantFromControls() });
    if (current !== version || response.revision !== current) return;
    const result = response.comparison;
    const change = result.change;
    const target = change.kind === 'assignment' ? change.symbol : `${change.symbol}(${change.arguments.join(', ')})`;
    const before = change.kind === 'relation' ? (change.before ? 'pertenece' : 'no pertenece') : change.before;
    const after = change.kind === 'relation' ? (change.after ? 'pertenece' : 'no pertenece') : change.after;
    $('comparison-status').textContent = `${target}: ${before} → ${after}. ${result.truth_changed ? 'Cambia el valor de verdad.' : 'El valor de verdad se mantiene.'} ${result.evidence_changes.length} pasos con cambios de evidencia.`;
    const changedIds = new Set(result.evidence_changes.map((change) => change.trace_id));
    $('comparison-results').replaceChildren(scenarioPanel('Original', result.before, changedIds),
      scenarioPanel('Con el cambio', result.after, changedIds));
    $('comparison-results').hidden = false;
  } catch (error) {
    if (current !== version) return;
    const issues = error.issues || [{ message: error.message }];
    $('comparison-errors').replaceChildren(...issues.map((issue) => node('li', issue.message)));
    $('comparison-errors').hidden = false;
    $('comparison-errors').focus();
    $('comparison-status').textContent = 'Variante no evaluada. El escenario base se conserva.';
  } finally {
    if (current === version) $('compare').disabled = false;
  }
}

export function clearComparison() {
  base = null;
  version += 1;
  targets = [];
  $('comparison-panel').hidden = true;
  $('comparison-target').replaceChildren();
  $('comparison-value').replaceChildren();
  $('comparison-before').textContent = '';
  $('comparison-after').textContent = '';
  $('comparison-results').replaceChildren();
  $('comparison-results').hidden = true;
  $('comparison-errors').replaceChildren();
  $('comparison-errors').hidden = true;
  $('comparison-status').textContent = 'Elige un único cambio.';
  $('compare').disabled = false;
}

export function setComparisonBase(data) {
  clearComparison();
  base = structuredClone(data);
  renderTargets();
}

export function initializeComparison() {
  $('open-comparison').addEventListener('click', () => {
    $('comparison-panel').hidden = false;
    $('comparison-target').focus();
    $('comparison-panel').scrollIntoView({ block: 'nearest' });
  });
  $('comparison-target').addEventListener('change', renderValue);
  $('comparison-value').addEventListener('input', invalidateVariant);
  $('comparison-value').addEventListener('change', invalidateVariant);
  $('compare').addEventListener('click', runComparison);
}
