// Ejecutar en la página local abierta: agent-browser eval --stdin < tests/ui/smoke.js
(async () => {
  const $ = (id) => document.getElementById(id);
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const until = async (predicate) => {
    const deadline = Date.now() + 5000;
    while (!predicate()) {
      if (Date.now() > deadline) throw new Error('Se agotó el tiempo de espera de la interfaz.');
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
  };
  const fill = (element, value) => {
    element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
  };
  const evaluate = async () => {
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
  };
  const load = (id = 'pertenencia') => {
    $('example-select').value = id;
    $('load-example').click();
  };
  const oldConfirm = window.confirm;
  const realFetch = window.fetch;
  window.confirm = () => true;
  try {
    load();
    assert(!$('language-config').open && !$('interpretation-config').open,
      'El ejemplo deja la configuración plegada y conserva el editor visible');
    assert(!$('example-note').hidden && $('domain-overview').textContent.includes('2')
      && $('predicates-overview').textContent.includes('P'),
    'La guía y el resumen de la interpretación muestran los datos cargados');
    await evaluate();
    assert(!$('result').hidden && $('result-value').textContent === 'Verdadero', 'Átomo verdadero calculado desde el formulario');
    assert($('result-reason').textContent.includes('(1)'), 'La explicación identifica la tupla realmente evaluada');

    $('assignment-0').value = '3';
    $('assignment-0').dispatchEvent(new Event('change', { bubbles: true }));
    assert($('result').hidden, 'Cambiar el entorno invalida el resultado anterior');
    assert(!$('example-note').hidden && $('environment-note').textContent.includes('x'),
      'Cambiar una asignación conserva la guía del ejemplo y el nombre de la variable');
    await evaluate();
    assert($('result-value').textContent === 'Falso' && $('errors').hidden, 'Falso válido se distingue de un error');

    const cases = [
      ['∃x P(x)', 'Verdadero', 'Testigo: x: 1'],
      ['∀x P(x)', 'Falso', 'Contraejemplo: x: 3'],
      ['∀x (P(x) ∨ ¬P(x))', 'Verdadero', 'Comprobados 3 de 3'],
      ['∃x (P(x) ∧ ¬P(x))', 'Falso', 'comprobados 3 de 3'],
    ];
    for (const [formula, value, reason] of cases) {
      fill($('formula'), formula);
      assert($('example-note').hidden, 'Editar la fórmula retira las instrucciones del ejemplo anterior');
      await evaluate();
      assert(!$('result').hidden && $('result-value').textContent === value
        && $('result-reason').textContent.includes(reason), `Evidencia real: ${formula}`);
      assert($('environment').children.length === 0, 'Fórmula cerrada no pide asignaciones');
    }
    $('evidence').querySelector('details').open = true;
    await until(() => $('evidence').querySelectorAll('details').length === 4);
    assert($('evidence').querySelectorAll('details').length === 4, 'Comprobación exhaustiva permite abrir sus tres asignaciones');

    fill($('formula'), 'P(𝑥) ∧ P(x,x)');
    await evaluate();
    assert(!$('errors').hidden && $('result').hidden, 'Error sintáctico bloquea resultado');
    $('error-list').querySelector('a').click();
    const editor = $('formula');
    assert(editor.value.slice(editor.selectionStart, editor.selectionEnd) === 'P(x,x)',
      'El error selecciona el rango correcto tras convertir Unicode a UTF-16');

    fill($('formula'), 'P(z)');
    await evaluate();
    assert($('error-list').textContent.includes('Falta asignar z'), 'Variable libre pendiente se informa sin valor de verdad');
    fill($('domain'), '');
    await evaluate();
    assert($('result').hidden && $('error-list').textContent.includes('D no puede estar vacío'), 'Dominio vacío rechazado desde el servidor real');
    assert($('interpretation-config').open, 'Un error abre automáticamente la configuración que lo contiene');
    $('interpretation-config').open = false;
    $('error-list').querySelector('a').click();
    assert($('interpretation-config').open && document.activeElement === $('domain'),
      'El enlace de error vuelve a abrir la sección y enfoca el campo');

    load();
    const name = [...document.querySelectorAll('#symbols input[type=text]')].find((input) => input.value === 'P');
    fill(name, '__proto__');
    name.dispatchEvent(new Event('change', { bubbles: true }));
    fill($('formula'), '__proto__(x)');
    await evaluate();
    assert(!$('result').hidden && $('result-value').textContent === 'Verdadero', 'Nombre personalizado conserva su tabla sin colisión con objetos JavaScript');

    load('funcion');
    const remove = [...document.querySelectorAll('button')].find((button) => button.getAttribute('aria-label') === 'Quitar fila 9 de f');
    remove.click();
    await evaluate();
    assert($('result').hidden && $('error-list').textContent.includes('Falta definir f(c, c)'),
      'Función parcial bloquea incluso una fórmula que no la usa');

    load();
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
    fill($('formula'), '¬P(x)');
    release();
    await until(() => !$('evaluate').disabled);
    assert($('result').hidden && $('result-state').textContent.includes('Cambiaste los datos'),
      'Una respuesta tardía nunca reemplaza el contexto editado');

    window.fetch = realFetch;
    while ($('symbols').querySelector('button')) $('symbols').querySelector('button').click();
    fill($('domain'), 'uno\ndos');
    $('add-predicate').click();
    const customName = $('symbols').querySelector('input[type=text]');
    fill(customName, 'Listo');
    customName.dispatchEvent(new Event('change', { bubbles: true }));
    $('interpretations').querySelector('button').click();
    fill($('interpretations').querySelector('select'), 'uno');
    fill($('formula'), 'Listo(z)');
    $('analyze').click();
    await until(() => !$('analyze').disabled);
    $('assignment-0').value = 'uno';
    $('assignment-0').dispatchEvent(new Event('change', { bubbles: true }));
    await evaluate();
    assert(!$('result').hidden && $('result-value').textContent === 'Verdadero',
      'Lenguaje, dominio, tupla y entorno propios se configuran desde cero');
    $('interpretations').querySelector('button').click();
    await evaluate();
    assert($('result').hidden && $('error-list').textContent.includes('La relación Listo está vacía'),
      'Relación vacía se rechaza sin perder la fórmula del usuario');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
    window.fetch = realFetch;
  }
})()
