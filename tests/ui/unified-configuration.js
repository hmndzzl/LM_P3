// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
  const { inputData } = await import('/js/editors.js');
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const until = async (predicate) => {
    const deadline = Date.now() + 6000;
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
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    $('clear-example').click();
    fill($('domain'), 'a\nb');
    $('add-constant').click();
    const constant = $('constants-overview').querySelector('.symbol-card');
    fill(constant.querySelector('input[type=text]'), 'c');
    fill(constant.querySelector('.interpretation select'), 'a');
    assert(constant.querySelector('input[type=number]').parentElement.hidden
      && !constant.querySelector('.interpretation').textContent.includes('Tupla vacía')
      && !constant.querySelector('.interpretation button'),
      'La constante se configura con nombre y elemento de D, sin aridad ni filas vacías');
    assert(JSON.stringify(inputData(0).functions) === '[["c",0]]'
      && JSON.stringify(inputData(0).function_rows.c) === '[[[],"a"]]',
      'La interfaz conserva el contrato existente de M1/M2 para las constantes');
    $('add-predicate').click();
    const predicate = $('predicates-overview').querySelector('.symbol-card');
    fill(predicate.querySelector('input[type=text]'), 'P');
    predicate.querySelector('.interpretation button').click();
    fill(predicate.querySelector('.interpretation select'), 'a');
    await until(() => [...document.querySelectorAll('.symbol-editor')].filter((editor) => editor.open).length === 1);
    assert(!$('constants-overview').querySelector('details').open && predicate.querySelector('details').open,
      'Solo permanece abierto el editor del símbolo seleccionado');
    fill($('formula'), 'P(c)');
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
    assert(!$('result').hidden && $('result-value').dataset.value === 'true',
      'Una constante declarada desde cero se evalúa con el motor real');
    $('open-comparison').click();
    assert($('comparison-panel').parentElement.classList.contains('work-area')
      && $('comparison-panel').previousElementSibling.classList.contains('result-panel'),
      'La comparación sigue al resultado dentro de la columna de trabajo');
    const originalFormula = $('formula').value;
    fill($('comparison-new-value'), 'b');
    assert(!$('result').hidden && !$('comparison-panel').hidden && $('formula').value === originalFormula,
      'Editar la copia no invalida el formulario original aunque comparta la columna');
    $('compare').click();
    await until(() => !$('compare').disabled);
    assert([...$('comparison-results').querySelectorAll('.truth')].map((item) => item.textContent).join('|') === 'Verdadero|Falso',
      'Cambiar la constante compara resultados sin alterar el original');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
