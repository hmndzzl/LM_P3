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
  const load = (id) => {
    $('example-select').value = id;
    $('load-example').click();
  };
  const evaluate = async () => {
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
  };
  const assertEmpty = () => {
    const data = inputData(0);
    assert(!data.formula && !data.domain.length && !data.functions.length && !data.predicates.length
      && !data.assignments.length && !Object.keys(data.function_rows).length && !Object.keys(data.relations).length,
    'Limpiar borra todos los datos enviados al motor');
    assert(!$('symbols').querySelector('.symbol-card') && !$('environment').children.length
      && $('result').hidden && !$('evidence').children.length && !$('result-value').textContent,
    'Limpiar borra los editores, resultado y evidencia');
    assert($('comparison-panel').hidden && !$('comparison-target').children.length
      && !$('comparison-value').children.length && !$('comparison-results').children.length
      && !$('comparison-errors').children.length && $('errors').hidden,
    'Limpiar retira la base, controles y errores de comparación');
    assert($('example-note').hidden && !$('example-note').textContent
      && $('result-state').textContent === 'Sin evaluar', 'Limpiar retira la guía del ejemplo y restablece el estado');
  };
  const oldConfirm = window.confirm;
  const realFetch = window.fetch;
  window.confirm = () => true;
  try {
    const cases = [
      ['pertenencia', true], ['universal', false], ['universal-completo', true], ['relaciones', true],
      ['testigo', true], ['contradiccion', false], ['constante', true],
      ['constante-relacion', true], ['funcion', false], ['integrado', false], ['socrates', true],
    ];
    assert($('example-select').options.length === cases.length, 'El selector ofrece todos los ejemplos y variantes documentados');
    for (const [id, expected] of cases) {
      load(id);
      assert(!$('example-note').textContent.includes('Notas del curso') && $('example-note').querySelectorAll('p').length === 2 && !$('example-note').hidden,
        `El ejemplo ${id} muestra explicación y práctica sin la línea de referencia`);
      await evaluate();
      assert($('errors').hidden && !$('result').hidden && $('result-value').dataset.value === String(expected),
        `El motor calcula el resultado esperado de ${id}`);
    }
    load('funcion');
    const originalRows = JSON.stringify(inputData(0).function_rows.f);
    const output = document.querySelector('[id^="output-"]');
    output.value = 'c';
    output.dispatchEvent(new Event('input', { bubbles: true }));
    load('funcion');
    assert(JSON.stringify(inputData(0).function_rows.f) === originalRows,
      'Recargar reconstruye las tablas sin conservar cambios en el catálogo');
    load('pertenencia');
    await evaluate();
    $('open-comparison').click();
    $('comparison-target').value = [...$('comparison-target').options].find((option) => option.dataset.kind === 'assignment').value;
    $('comparison-target').dispatchEvent(new Event('change', { bubbles: true }));
    assert($('comparison-target').selectedOptions[0].textContent === 'x: 1',
      'El comparador también usa dos puntos para las asignaciones');
    $('comparison-new-value').value = '3';
    $('comparison-new-value').dispatchEvent(new Event('change', { bubbles: true }));
    $('compare').click();
    await until(() => !$('compare').disabled);
    assert(!$('comparison-results').hidden, 'La prueba de limpieza parte de una comparación real');
    window.confirm = () => false;
    $('clear-example').click();
    assert(!$('result').hidden && $('formula').value === 'P(x)', 'Cancelar la limpieza conserva el trabajo');
    $('example-select').value = 'constante';
    $('load-example').click();
    assert($('formula').value === 'P(x)', 'Cancelar otra carga conserva el ejemplo actual');
    window.confirm = () => true;
    $('clear-example').click();
    assertEmpty();
    load('pertenencia');
    let release;
    let waiting = false;
    window.fetch = async (...args) => {
      const response = await realFetch(...args);
      if (String(args[0]).endsWith('/api/evaluate')) {
        waiting = true;
        await new Promise((resolve) => { release = resolve; });
      }
      return response;
    };
    $('workspace').requestSubmit();
    await until(() => waiting);
    $('clear-example').click();
    release();
    await until(() => !$('evaluate').disabled);
    assertEmpty();
    window.fetch = realFetch;
    load('constante');
    await evaluate();
    assert($('result-value').dataset.value === 'true' && $('errors').hidden,
      'Después de limpiar se puede cargar y evaluar otro ejemplo');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
    window.fetch = realFetch;
  }
})()
