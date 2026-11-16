// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
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
  const change = (element, value) => {
    element.value = value;
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    $('example-select').value = 'universal';
    $('load-example').click();
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
    $('open-comparison').click();
    assert(!$('comparison-kind') && !$('comparison-panel').querySelector('input[type=checkbox]'),
      'Se elige el dato directamente, sin selector de tipo ni casilla de pertenencia');
    assert($('comparison-formula').textContent === '∀x P(x)'
      && $('comparison-original-result').textContent === 'Resultado original: Falso.',
      'La comparación identifica la fórmula y el resultado que se conservaron');
    assert($('comparison-environment').textContent.includes('Fórmula cerrada'),
      'La comparación distingue una fórmula cerrada de un entorno con asignaciones');
    assert($('comparison-suggestions').firstElementChild.textContent === 'Añadir (3) a P'
      && $('comparison-suggestions').firstElementChild.getAttribute('aria-pressed') === 'true',
      'Se propone primero un cambio sobre el contraejemplo devuelto por el motor');
    assert([...$('comparison-suggestions').children].every((button) => !button.textContent.includes(' a R') && !button.textContent.includes(' de R')),
      'Las sugerencias no incluyen la relación R que no intervino en esta evaluación');
    change($('comparison-arg-0'), '1');
    assert($('comparison-before').textContent === '(1) pertenece a P.'
      && $('comparison-after').textContent === 'Quitar (1) de P.', 'El cambio de una relación se describe como una acción concreta');
    change($('comparison-arg-0'), '3');
    assert($('comparison-before').textContent === '(3) no pertenece a P.'
      && $('comparison-after').textContent === 'Añadir (3) a P.' && !$('compare').disabled,
      'Elegir una tupla ausente propone añadirla');
    $('compare').click();
    await until(() => !$('compare').disabled);
    assert([...$('comparison-results').querySelectorAll('.truth')].map((item) => item.textContent).join('|') === 'Falso|Verdadero',
      'Añadir la tupla compara los dos resultados calculados por el motor');
    assert($('result-value').textContent === 'Falso', 'La comparación conserva el resultado original');
    $('example-select').value = 'constante';
    $('load-example').click();
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
    $('open-comparison').click();
    change($('comparison-target'), [...$('comparison-target').options].find((option) => option.dataset.kind === 'function').value);
    assert($('compare').disabled && $('comparison-status').textContent.includes('diferente al original'),
      'Una imagen sin cambios no se anuncia como modificada ni permite comparar');
    change($('comparison-new-value'), 'b');
    assert(!$('compare').disabled && $('comparison-after').textContent === 'Valor de i: b',
      'Seleccionar una imagen diferente habilita la comparación y muestra la propuesta');
    change($('comparison-new-value'), 'a');
    assert($('compare').disabled, 'Restaurar el valor original vuelve a deshabilitar la comparación');
    $('example-select').value = 'constante-relacion';
    $('load-example').click();
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
    $('open-comparison').click();
    change($('comparison-target'), [...$('comparison-target').options].find((option) => option.textContent === 'Q').value);
    change($('comparison-arg-0'), 'a');
    change($('comparison-arg-1'), 'c');
    assert($('comparison-before').textContent === '(a, c) pertenece a Q.',
      'La pertenencia de Q(a,c) coincide con la interpretación realmente evaluada');
    const q = [...document.querySelectorAll('.symbol-card')].find((card) => card.querySelector('input[type=text]').value === 'Q');
    q.querySelector('details').open = true;
    q.querySelector('[aria-label="Quitar fila 3 de Q"]').click();
    assert($('comparison-panel').hidden && $('result').hidden,
      'Editar la interpretación descarta el contexto de comparación anterior');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
