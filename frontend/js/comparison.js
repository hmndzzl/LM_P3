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

function invalidateVariant() {
  version += 1;
  $('comparison-results').hidden = true;
  $('comparison-errors').hidden = true;
  $('comparison-status').textContent = 'Variante modificada. Evalúala para comparar.';
  $('compare').disabled = !targets.length;
}

function renderValue() {
  $('comparison-value').replaceChildren();
  const target = targets[Number($('comparison-target').value)];
  if (!target) return;
  const kind = $('comparison-kind').value;
  if (kind !== 'relation') {
    const label = node('label', `Nuevo valor (en la base: ${target.before})`);
    label.append(valueSelect(target.before, 'comparison-new-value'));
    $('comparison-value').append(label);
    return;
  }
  const tupleFields = node('div');
  tupleFields.className = 'tuple-row';
  for (let index = 0; index < target.arity; index += 1) {
    const label = node('label', `Argumento ${index + 1}`);
    const select = valueSelect(base.domain[0], `comparison-arg-${index}`);
    select.addEventListener('change', syncMembership);
    label.append(select);
    tupleFields.append(label);
  }
  if (target.arity === 0) tupleFields.append(node('p', 'Tupla vacía ()'));
  const label = node('label');
  const checkbox = node('input');
  checkbox.type = 'checkbox';
  checkbox.id = 'comparison-member';
  label.append(checkbox, document.createTextNode('La tupla pertenece a la relación en la variante'));
  $('comparison-value').append(tupleFields, node('p'), label);
  $('comparison-value').children[1].id = 'comparison-membership';
  syncMembership();
}

function relationArguments() {
  const target = targets[Number($('comparison-target').value)];
  return Array.from({ length: target.arity }, (_, index) => $(`comparison-arg-${index}`).value);
}

function syncMembership() {
  const target = targets[Number($('comparison-target').value)];
  const key = JSON.stringify(relationArguments());
  const member = base.relations[target.symbol].some((row) => JSON.stringify(row) === key);
  $('comparison-member').checked = member;
  $('comparison-membership').textContent = `En la base, esta tupla ${member ? 'pertenece' : 'no pertenece'} a ${target.symbol}.`;
}

function renderTargets() {
  const kind = $('comparison-kind').value;
  if (kind === 'function') {
    targets = base.functions.flatMap(([symbol]) => base.function_rows[symbol].map(([arguments_, before], index) =>
      ({ symbol, arguments: arguments_, before, index, label: `${symbol}(${arguments_.join(', ')}) → ${before}` })));
  } else if (kind === 'assignment') {
    targets = base.assignments.map(([symbol, before], index) => ({ symbol, before, index, label: `${symbol}: ${before}` }));
  } else {
    targets = base.predicates.map(([symbol, arity]) => ({ symbol, arity, label: symbol }));
  }
  $('comparison-target').replaceChildren();
  targets.forEach((target, index) => $('comparison-target').append(new Option(target.label, String(index))));
  if (!targets.length) $('comparison-target').append(new Option('No hay datos de este tipo', ''));
  renderValue();
  invalidateVariant();
}

function variantFromControls() {
  const variant = structuredClone(base);
  const kind = $('comparison-kind').value;
  const target = targets[Number($('comparison-target').value)];
  if (kind === 'function') {
    variant.function_rows[target.symbol][target.index][1] = $('comparison-new-value').value;
  } else if (kind === 'assignment') {
    variant.assignments[target.index][1] = $('comparison-new-value').value;
  } else {
    const args = relationArguments();
    const rows = variant.relations[target.symbol];
    const index = rows.findIndex((row) => JSON.stringify(row) === JSON.stringify(args));
    if ($('comparison-member').checked && index < 0) rows.push(args);
    if (!$('comparison-member').checked) {
      variant.relations[target.symbol] = rows.filter((row) => JSON.stringify(row) !== JSON.stringify(args));
    }
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
    $('comparison-status').textContent = `${target}: ${before} → ${after}. ${result.truth_changed ? 'Cambia el valor de verdad.' : 'El valor de verdad se mantiene.'} ${result.evidence_changes.length} instancias de evidencia modificadas.`;
    const changedIds = new Set(result.evidence_changes.map((change) => change.trace_id));
    $('comparison-results').replaceChildren(scenarioPanel('Escenario base', result.before, changedIds),
      scenarioPanel('Variante', result.after, changedIds));
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
  $('comparison-kind').value = base.functions.length ? 'function' : 'relation';
  renderTargets();
}

export function initializeComparison() {
  $('open-comparison').addEventListener('click', () => {
    $('comparison-panel').hidden = false;
    $('comparison-kind').focus();
    $('comparison-panel').scrollIntoView({ block: 'nearest' });
  });
  $('comparison-kind').addEventListener('change', renderTargets);
  $('comparison-target').addEventListener('change', renderValue);
  $('comparison-panel').addEventListener('input', invalidateVariant);
  $('compare').addEventListener('click', runComparison);
}
