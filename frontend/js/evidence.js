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
    negation: `La subfórmula es ${trace.children[0]?.value ? 'verdadera' : 'falsa'}. Al negarla, el resultado es ${trace.value ? 'verdadero' : 'falso'}.`,
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

function stepSection(title, content, className = '') {
  const section = node('div');
  section.className = `step-section ${className}`;
  const heading = node('strong', title);
  heading.className = 'step-heading';
  section.append(heading, content);
  return section;
}

function evidenceNode(trace, context, path = '1') {
  const details = node('details');
  details.className = 'trace-step';
  details.dataset.value = String(trace.value);
  const changed = context.changedIds.has(trace.trace_id);
  details.classList.toggle('evidence-changed', changed);
  const summary = node('summary');
  const number = node('span', `Paso ${path}`);
  number.className = 'step-number';
  const formula = node('span', trace.formula);
  formula.className = 'step-formula';
  const result = node('span', trace.value ? 'Verdadero' : 'Falso');
  result.className = 'step-result';
  result.dataset.value = String(trace.value);
  result.setAttribute('aria-label', `Resultado calculado: ${result.textContent}`);
  summary.append(number, document.createTextNode(' '), formula, document.createTextNode(' '));
  if (trace.environment.length) {
    const values = node('span', environmentText(trace));
    values.className = 'step-context';
    summary.append(values, document.createTextNode(' '));
  }
  summary.append(result);
  if (changed) summary.append(node('span', 'Evidencia modificada'));
  summary.addEventListener('click', () => selectStep(trace, context, path));
  details.append(summary);
  // El contenido se crea al abrir el paso; los resultados ya proceden del motor.
  details.addEventListener('toggle', () => {
    if (!details.open || details.dataset.loaded) return;
    selectStep(trace, context, path);
    details.dataset.loaded = 'true';
    if (trace.environment.length) {
      const values = node('div');
      values.className = 'step-values';
      for (const [name, value] of trace.environment) values.append(node('span', `${name}: ${value}`));
      details.append(stepSection('Asignaciones', values));
    }
    const lookups = trace.terms.filter((term) => term.reason !== 'variable_assignment');
    if (lookups.length) {
      const terms = node('ul');
      for (const term of lookups) terms.append(termNode(term));
      details.append(stepSection('Evaluación de términos', terms));
    }
    if (trace.children.length) {
      const children = node('div');
      children.className = 'step-children';
      trace.children.forEach((child, index) => children.append(evidenceNode(child, context, `${path}.${index + 1}`)));
      const heading = trace.variable
        ? `Comprobaciones de ${trace.variable} · ${trace.checked_elements.length} de ${trace.domain_size} valores`
        : 'Subfórmulas evaluadas';
      details.append(stepSection(heading, children, 'step-checks'));
    }
    const conclusion = stepSection('Conclusión', node('p', reasonText(trace)), 'step-conclusion');
    if (trace.unvisited_elements.length) {
      const decisive = trace.reason === 'existential_witness' ? 'un testigo' : 'un contraejemplo';
      const skipped = node('p', `No fue necesario probar ${trace.variable}: ${trace.unvisited_elements.join(', ')}; ya se encontró ${decisive}. Esto no significa que los casos omitidos sean falsos.`);
      skipped.className = 'help';
      conclusion.append(skipped);
    }
    details.append(conclusion);
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
