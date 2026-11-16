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
    assert($('compare').disabled && $('comparison-status').textContent.includes('diferente al original'),
      'Una imagen sin cambios no se anuncia como modificada ni permite comparar');
    change($('comparison-new-value'), 'b');
    assert(!$('compare').disabled && $('comparison-after').textContent === 'i() → b',
      'Seleccionar una imagen diferente habilita la comparación y muestra la propuesta');
    change($('comparison-new-value'), 'a');
    assert($('compare').disabled, 'Restaurar el valor original vuelve a deshabilitar la comparación');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
