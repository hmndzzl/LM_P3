const $ = (id) => document.getElementById(id);

function node(tag, text = '') {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
}

export function reasonText(trace) {
  const checked = trace.checked_elements.length;
  const tuple = `(${trace.terms.map((term) => term.value).join(', ')})`;
  const predicate = trace.formula.split('(')[0];
  const reasons = {
    predicate_member: `La tupla ${tuple} pertenece a ${predicate}.`,
    predicate_not_member: `La tupla ${tuple} no pertenece a ${predicate}.`,
    negation: 'La negación invierte el valor de su subfórmula.',
    conjunction: 'La conjunción es verdadera cuando ambos operandos son verdaderos.',
    disjunction: 'La disyunción es verdadera cuando al menos un operando es verdadero.',
    implication: 'La implicación solo es falsa con antecedente verdadero y consecuente falso.',
    biconditional: 'El bicondicional es verdadero cuando ambos operandos tienen el mismo valor.',
    existential_witness: `Testigo: ${trace.variable}: ${trace.decisive_element}. La condición es verdadera con ese valor; basta un caso para confirmar que existe.`,
    universal_counterexample: `Contraejemplo: ${trace.variable}: ${trace.decisive_element}. La condición es falsa con ese valor; basta un caso para refutar «para todo ${trace.variable}».`,
    universal_complete: `Comprobados ${checked} de ${trace.domain_size} elementos. La condición fue verdadera para cada valor de ${trace.variable}.`,
    existential_complete: `Ningún elemento cumple la condición: comprobados ${checked} de ${trace.domain_size}. La condición fue falsa en todos los casos.`,
  };
  return reasons[trace.reason] || 'Consulta la evidencia de las subfórmulas.';
}

function environmentText(trace) {
  return trace.environment.map(([name, value]) => `${name}: ${value}`).join(', ');
}

function selectStep(trace, context, path) {
  const characters = Array.from(context.formula);
  context.formulaTarget.replaceChildren();
  if (trace.span) {
    context.formulaTarget.append(document.createTextNode(characters.slice(0, trace.span.start).join('')));
    context.formulaTarget.append(node('mark', characters.slice(trace.span.start, trace.span.end).join('')));
    context.formulaTarget.append(document.createTextNode(characters.slice(trace.span.end).join('')));
  } else {
    context.formulaTarget.textContent = context.formula;
  }
  context.selectionTarget.textContent = `Paso ${path}: ${trace.formula}. ${trace.environment.length ? `Valores: ${environmentText(trace)}.` : 'Sin variables asignadas al entrar.'}`;
}

function termNode(term) {
  const separator = term.reason === 'variable_assignment' ? ':' : ' →';
  const item = node('li', `${term.term}${separator} ${term.value} · ${term.reason === 'variable_assignment' ? 'asignación de variable' : 'consulta de función'}`);
  if (term.children.length) {
    const children = node('ul');
    for (const child of term.children) children.append(termNode(child));
    item.append(children);
  }
  return item;
}

function evidenceNode(trace, context, path = '1') {
  const details = node('details');
  const changed = context.changedIds.has(trace.trace_id);
  details.classList.toggle('evidence-changed', changed);
  const summary = node('summary', `Paso ${path} · ${trace.formula}${trace.environment.length ? ` · ${environmentText(trace)}` : ''} — ${trace.value ? 'Verdadero' : 'Falso'}${changed ? ' · evidencia modificada' : ''}`);
  summary.addEventListener('click', () => selectStep(trace, context, path));
  details.append(summary);
  // El detalle se crea al abrirlo para no dibujar toda una traza grande de golpe.
  details.addEventListener('toggle', () => {
    if (!details.open || details.dataset.loaded) return;
    selectStep(trace, context, path);
    details.dataset.loaded = 'true';
    details.append(node('p', reasonText(trace)));
    details.append(node('p', trace.environment.length
      ? `Valores al entrar a este paso: ${environmentText(trace)}.`
      : 'Sin variables asignadas al entrar a este paso.'));
    if (trace.terms.length) {
      const terms = node('ul');
      for (const term of trace.terms) terms.append(termNode(term));
      details.append(terms);
    }
    if (trace.variable) {
      details.append(node('p', `Valores probados de ${trace.variable}: ${trace.checked_elements.join(', ')}. Cada paso interior comprueba la condición con uno de esos valores.`));
    }
    if (trace.unvisited_elements.length) {
      const decisive = trace.reason === 'existential_witness' ? 'un testigo' : 'un contraejemplo';
      details.append(node('p', `No fue necesario probar ${trace.variable}: ${trace.unvisited_elements.join(', ')}; ya se encontró ${decisive}. Esto no significa que los casos omitidos sean falsos.`));
    }
    trace.children.forEach((child, index) => details.append(evidenceNode(child, context, `${path}.${index + 1}`)));
  });
  return details;
}

export function createEvidence(trace, formula, formulaTarget, selectionTarget, changedIds = new Set()) {
  return evidenceNode(trace, { formula, formulaTarget, selectionTarget, changedIds });
}

export function showResult(formula, result) {
  $('result-formula').textContent = formula;
  $('result-value').textContent = result.value ? 'Verdadero' : 'Falso';
  $('result-value').dataset.value = String(result.value);
  $('result-reason').textContent = reasonText(result.trace);
  $('evidence-selection').textContent = 'Selecciona un paso para resaltar su subfórmula.';
  $('evidence').replaceChildren(createEvidence(result.trace, formula, $('result-formula'), $('evidence-selection')));
  $('empty-result').hidden = true;
  $('result').hidden = false;
  $('result-state').textContent = `Evaluación completada: ${result.value ? 'Verdadero' : 'Falso'}.`;
  document.querySelector('.result-panel').scrollIntoView({ block: 'nearest' });
}
