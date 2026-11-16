// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
  const checks = [];
  const assert = (value, message) => {
    if (!value) throw new Error(message);
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
  const evaluate = async (formula) => {
    if (formula) fill($('formula'), formula);
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
  };
  const compare = async () => {
    $('compare').click();
    await until(() => !$('compare').disabled);
  };
  const load = (id = 'pertenencia') => {
    $('example-select').value = id;
    $('load-example').click();
  };
  const oldConfirm = window.confirm;
  const realFetch = window.fetch;
  window.confirm = () => true;
  try {
    assert(document.title.startsWith('Evaluador semántico'), 'Nombre actualizado de la aplicación');
    load();
    const editor = $('formula');
    const buttons = [...$('symbol-toolbar').querySelectorAll('button')];
    assert(buttons.map((button) => button.textContent).join('') === '¬∧∨→↔∀∃()', 'Nueve botones lógicos disponibles');
    for (const button of buttons) {
      fill(editor, 'P(x)');
      editor.focus();
      editor.setSelectionRange(1, 3);
      button.click();
      assert(editor.value === `P${button.textContent})` && document.activeElement === editor,
        `Inserción y selección: ${button.textContent}`);
    }
    document.execCommand('undo');
    assert(editor.value === 'P(x)', 'Deshacer restaura la selección reemplazada');
    document.execCommand('redo');
    assert(editor.value === 'P))', 'Rehacer recupera la inserción lógica');

    load('funcion');
    const functionTable = [...document.querySelectorAll('.interpretation')].find((section) => section.querySelector('h3').textContent.startsWith('f'));
    assert(functionTable.querySelector('select').options.length === 4, 'Las tuplas usan selectores del dominio');
    assert(functionTable.querySelector('.help').textContent.includes('Faltan 0'), 'Conteo de salidas funcionales completas');
    fill($('domain'), 'a\nb');
    assert([...document.querySelectorAll('#interpretations option')].some((option) => option.textContent === 'c (fuera de D)'),
      'Editar el dominio conserva valores recuperables fuera de D');
    await evaluate();
    const outputIssue = [...$('error-list').querySelectorAll('a')].find((link) => link.textContent.includes('salida'));
    assert(Boolean(outputIssue), 'Salida fuera del dominio se rechaza');
    outputIssue.click();
    assert(document.activeElement.id.startsWith('output-'), 'Error funcional enfoca la salida exacta');

    load('funcion');
    await evaluate('P(x,f(x,f(x,y)))');
    $('evidence').querySelector('details').open = true;
    await until(() => $('evidence').querySelector('ul ul ul'));
    assert($('evidence').textContent.includes('asignación de variable'), 'Los términos anidados exponen todas las consultas');
    load();
    await evaluate('∀𝑥 (P(𝑥) ∨ ¬P(𝑥))');
    $('evidence').querySelector('details').open = true;
    await until(() => $('evidence').querySelectorAll('details').length > 1);
    $('evidence').querySelectorAll('details')[1].open = true;
    await until(() => $('result-formula').querySelector('mark')?.textContent.startsWith('('));
    assert($('result-formula').querySelector('mark').textContent === '(P(𝑥) ∨ ¬P(𝑥))',
      'Seleccionar una instancia resalta su subfórmula original Unicode');

    load('funcion');
    await evaluate('P(f(x,y),y)');
    $('open-comparison').click();
    fill($('comparison-target'), '4');
    fill($('comparison-new-value'), 'a');
    await compare();
    assert(!$('comparison-results').hidden && $('comparison-status').textContent.includes('Cambia el valor de verdad'),
      'Cambiar una salida compara Falso con Verdadero');
    assert($('result-value').textContent === 'Falso' && $('result-reason').textContent.includes('(b, b)'),
      'La comparación conserva el resultado base y la interpretación original');
    assert($('comparison-results').querySelectorAll('.evidence-changed').length === 2,
      'Las instancias afectadas quedan identificadas en ambos escenarios');

    load();
    await evaluate('∃x P(x)');
    $('open-comparison').click();
    fill($('comparison-kind'), 'relation');
    $('comparison-member').checked = false;
    $('comparison-member').dispatchEvent(new Event('input', { bubbles: true }));
    await compare();
    assert($('comparison-status').textContent.includes('se mantiene'), 'Cambiar el testigo conserva la verdad');
    assert($('comparison-results').textContent.includes('Testigo: x: 1')
      && $('comparison-results').textContent.includes('Testigo: x: 2'), 'Los dos testigos proceden de evaluaciones reales');

    load();
    await evaluate();
    $('open-comparison').click();
    fill($('comparison-kind'), 'assignment');
    fill($('comparison-new-value'), '3');
    await compare();
    assert($('comparison-status').textContent.includes('Cambia el valor de verdad'), 'Comparación de asignación libre');
    fill($('formula'), '¬P(x)');
    assert($('comparison-panel').hidden && $('result').hidden, 'Editar el contexto obliga a renovar la base');

    load();
    [...document.querySelectorAll('button')].find((button) => button.getAttribute('aria-label') === 'Quitar fila 2 de P').click();
    await evaluate('∃x P(x)');
    $('open-comparison').click();
    fill($('comparison-kind'), 'relation');
    $('comparison-member').checked = false;
    $('comparison-member').dispatchEvent(new Event('input', { bubbles: true }));
    await compare();
    assert(!$('comparison-errors').hidden && $('comparison-results').hidden && !$('result').hidden,
      'Variante que vacía la relación se rechaza y preserva el original');

    load();
    await evaluate();
    $('open-comparison').click();
    await compare();
    assert(!$('comparison-errors').hidden && $('comparison-errors').textContent.includes('exactamente un dato'),
      'Una variante sin cambios no se presenta como comparación válida');
    fill($('comparison-kind'), 'assignment');
    fill($('comparison-new-value'), '3');
    let release;
    let waiting = false;
    let delivered = false;
    window.fetch = async (...args) => {
      const response = await realFetch(...args);
      if (!String(args[0]).endsWith('/api/compare')) return response;
      const data = await response.json();
      waiting = true;
      await new Promise((resolve) => { release = resolve; });
      return { ok: response.ok, json: async () => { delivered = true; return data; } };
    };
    $('compare').click();
    await until(() => waiting);
    fill($('comparison-new-value'), '1');
    release();
    await until(() => delivered);
    assert($('comparison-results').hidden && $('comparison-status').textContent.includes('Variante modificada'),
      'Una comparación tardía no sobrescribe una variante editada');
    window.fetch = realFetch;

    while ($('symbols').querySelector('button')) $('symbols').querySelector('button').click();
    fill($('domain'), 'único');
    $('add-function').click();
    fill($('symbols').querySelector('input[type=text]'), 'c');
    fill($('symbols').querySelector('input[type=number]'), '0');
    $('interpretations').querySelector('button').click();
    fill($('interpretations').querySelector('select'), 'único');
    $('add-predicate').click();
    const predicateRow = $('symbols').lastElementChild;
    fill(predicateRow.querySelector('input[type=text]'), 'T');
    fill(predicateRow.querySelector('input[type=number]'), '0');
    $('interpretations').lastElementChild.querySelector('button').click();
    await evaluate('T ↔ T()');
    assert(!$('result').hidden && $('result-value').textContent === 'Verdadero',
      'Símbolos de aridad cero se configuran y evalúan desde la interfaz');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
    window.fetch = realFetch;
  }
})()
