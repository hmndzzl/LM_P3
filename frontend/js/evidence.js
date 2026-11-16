const $ = (id) => document.getElementById(id);

function node(tag, text = '') {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
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

export function showResult(formula, result) {
  $('result-formula').textContent = formula;
  $('result-value').textContent = result.value ? 'Verdadero' : 'Falso';
  $('result-value').dataset.value = String(result.value);
  $('result-reason').textContent = reasonText(result.trace);
  $('evidence').replaceChildren(evidenceNode(result.trace));
  $('empty-result').hidden = true;
  $('result').hidden = false;
  $('result-state').textContent = `Evaluación completada: ${result.value ? 'Verdadero' : 'Falso'}.`;
}
