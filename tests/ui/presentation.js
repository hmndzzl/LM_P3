// Ensayo técnico reproducible: interfaz y respuestas reales, sin sustituir al motor.
(async () => {
  const $ = (id) => document.getElementById(id);
  const { inputData } = await import('/js/editors.js');
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const until = async (predicate) => {
    const deadline = Date.now() + 8000;
    while (!predicate()) {
      if (Date.now() > deadline) throw new Error('Tiempo de espera agotado.');
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
  };
  const fill = (element, value) => {
    element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };
  const load = (id) => {
    $('example-select').value = id;
    $('load-example').click();
  };
  let evaluation;
  let comparison;
  let failure;
  const evaluate = async () => {
    evaluation = null;
    failure = null;
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
  };
  const compare = async (label, value) => {
    $('comparison-custom').open = true;
    const option = [...$('comparison-target').options].find((item) => item.textContent === label);
    if (!option) throw new Error(`No se encontró ${label}.`);
    fill($('comparison-target'), option.value);
    fill($('comparison-new-value'), value);
    comparison = null;
    $('compare').click();
    await until(() => !$('compare').disabled);
  };
  const originalConfirm = window.confirm;
  const originalFetch = window.fetch;
  window.confirm = () => true;
  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    const body = await response.clone().json();
    if (body.status === 'evaluated') evaluation = body.evaluation;
    if (body.status === 'compared') comparison = body.comparison;
    if (!response.ok) failure = body;
    return response;
  };
  try {
    load('universal-completo');
    await evaluate();
    assert(evaluation?.value === true && evaluation.trace.reason === 'universal_complete'
      && evaluation.trace.checked_elements.join(',') === '1,2,3',
    'El universal verdadero conserva la comprobación de los tres elementos');
    load('integrado');
    const originalRows = JSON.stringify(inputData(0).function_rows);
    await evaluate();
    assert(evaluation?.value === false && evaluation.trace.reason === 'conjunction',
      'El caso integrado parte de una conjunción falsa calculada por el motor');
    const universal = evaluation.trace.children[0];
    assert(universal.reason === 'universal_counterexample' && universal.decisive_element === 'c'
      && universal.checked_elements.join(',') === 'a,b,c', 'El contraejemplo exterior es c, después de comprobar a y b');
    assert(universal.children[0].decisive_element === 'a' && universal.children[1].decisive_element === 'c',
      'Los testigos interiores iniciales son a para x: a y c para x: b');
    const existential = universal.children[2];
    assert(existential.reason === 'existential_complete' && existential.value === false
      && existential.checked_elements.join(',') === 'a,b,c', 'Para x: c el existencial falso conserva sus tres comprobaciones');
    const last = existential.children[2];
    assert(last.children[0].value === true && last.children[1].value === false
      && last.children[1].terms[0].value === 'a', 'Con x: c, y: c, Q es verdadera pero f(c,c) produce a y R(a) es falsa');
    assert(evaluation.trace.children[1].value === true && !$('environment').children.length,
      'La constante hace verdadera la negación y la fórmula cerrada no solicita entorno');
    $('open-comparison').click();
    await compare('Valor de f(c, c): a', 'b');
    assert(comparison?.truth_changed === true && !comparison.before.value && comparison.after.value
      && comparison.change.kind === 'function' && comparison.change.arguments.join(',') === 'c,c',
    'Cambiar solo f(c,c) de a a b transforma Falso en Verdadero');
    assert(comparison.after.trace.children[0].reason === 'universal_complete'
      && comparison.after.trace.children[0].children[2].decisive_element === 'c',
      'La variante justifica el universal completo y el nuevo testigo y: c');
    assert(JSON.stringify(inputData(0).function_rows) === originalRows && $('result-value').textContent === 'Falso',
      'La presentación conserva la tabla y el resultado originales después de comparar');
    await compare('Valor de f(a, a): b', 'c');
    assert(comparison?.truth_changed === false && !comparison.before.value && !comparison.after.value
      && comparison.evidence_changes.length > 0, 'Otro valor funcional cambia la evidencia aunque el resultado continúe siendo Falso');

    load('pertenencia');
    fill($('formula'), '∀x ((P(x) → P(x)) ↔ (P(x) ∨ ¬P(x)))');
    await evaluate();
    assert(evaluation?.value === true && evaluation.trace.checked_elements.length === 3,
      'Implicación, bicondicional, disyunción y negación se evalúan desde el editor');
    fill($('formula'), '∃x P(x) ∧ ¬P(x)');
    $('analyze').click();
    await until(() => !$('analyze').disabled);
    assert($('assignment-0') && $('result').hidden, 'Revisar variables libres prepara el entorno sin mostrar un valor de verdad');
    fill($('assignment-0'), '3');
    await evaluate();
    assert(evaluation?.value === true && inputData(0).assignments[0][1] === '3'
      && evaluation.trace.children[1].environment.some(([name, value]) => name === 'x' && value === '3'),
    'El alcance del existencial conserva la asignación libre exterior x: 3');
    fill($('formula'), '∃x (P(x) ∧ ¬P(x))');
    await evaluate();
    assert(evaluation?.value === false && !$('environment').children.length,
      'Ampliar el alcance con paréntesis cambia el resultado y elimina la asignación libre');

    const invalid = [
      ['dominio vacío', 'pertenencia', () => fill($('domain'), ''), 'invalid_domain'],
      ['sintaxis', 'pertenencia', () => fill($('formula'), 'P(x'), 'missing_parenthesis'],
      ['símbolo', 'pertenencia', () => fill($('formula'), 'Desconocido(x)'), 'unknown_symbol'],
      ['aridad', 'pertenencia', () => fill($('formula'), 'P(x,x)'), 'arity_mismatch'],
      ['asignación', 'pertenencia', () => fill($('formula'), 'P(z)'), 'missing_assignment'],
      ['tupla fuera de D', 'pertenencia', () => fill($('domain'), '1\n2'), 'outside_domain'],
      ['relación vacía', 'pertenencia', () => {
        while (document.querySelector('[aria-label^="Quitar fila"][aria-label$=" de P"]')) {
          document.querySelector('[aria-label^="Quitar fila"][aria-label$=" de P"]').click();
        }
      }, 'empty_interpretation'],
      ['función parcial', 'funcion', () => document.querySelector('[aria-label="Quitar fila 9 de f"]').click(), 'partial_function'],
      ['salidas incompatibles', 'funcion', () => {
        const table = $('functions-overview').querySelector('.interpretation');
        table.lastElementChild.click();
        const row = table.querySelectorAll('.tuple-row')[9];
        const fields = row.querySelectorAll('select');
        ['a', 'a', 'c'].forEach((value, index) => fill(fields[index], value));
      }, 'conflicting_function_row'],
    ];
    for (const [label, id, mutate, code] of invalid) {
      load(id);
      mutate();
      await evaluate();
      assert(failure?.errors.some((issue) => issue.code === code) && !('evaluation' in failure)
        && $('result').hidden && !$('errors').hidden, `Entrada inválida sin verdad: ${label}`);
      load(id);
      await evaluate();
      assert(evaluation && $('errors').hidden && !$('result').hidden, `Reparación comprobada: ${label}`);
    }
    return { passed: checks.length, checks };
  } finally {
    window.confirm = originalConfirm;
    window.fetch = originalFetch;
  }
})()
