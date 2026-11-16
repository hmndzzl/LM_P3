// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
  const { inputData } = await import('/js/editors.js');
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const load = (id) => {
    $('example-select').value = id;
    $('load-example').click();
  };
  const fill = (element, value) => {
    element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };
  const symbolRow = (name) => [...$('symbols').rows].find((row) => row.querySelector('input[type=text]').value === name);
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    load('pertenencia');
    $('language-config').open = true;
    const row = symbolRow('R');
    const arity = row.querySelector('input[type=number]');
    const original = inputData(0).relations.R;
    fill(arity, '5');
    let rows = inputData(0).relations.R;
    assert(rows.length === 3 && rows.every((args, index) => args.length === 5
      && args[0] === original[index][0] && args[1] === original[index][1] && args.slice(2).every((value) => value === '')),
    'Aumentar de dos a cinco conserva las parejas y añade tres argumentos vacíos');
    const table = [...document.querySelectorAll('.interpretation')].find((section) => section.querySelector('h3').textContent.startsWith('R ·'));
    assert([...table.querySelectorAll('.tuple-row')].every((tuple) => tuple.querySelectorAll('select').length === 5),
      'Todas las filas muestran cinco selectores, también las filas existentes');
    assert(getComputedStyle(row.cells[0]).whiteSpace === 'nowrap' && getComputedStyle(row.lastElementChild).whiteSpace === 'nowrap',
      'El tipo de símbolo y la acción se mantienen en una sola línea');
    for (const select of table.querySelectorAll('select')) if (!select.value) fill(select, '1');
    fill($('formula'), 'R(x,x,x,x,x)');
    $('workspace').requestSubmit();
    const deadline = Date.now() + 6000;
    while ($('evaluate').disabled) {
      if (Date.now() > deadline) throw new Error('Tiempo de espera agotado.');
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
    assert($('errors').hidden && !$('result').hidden, 'Las tuplas de cinco componentes se evalúan con el servidor real');
    window.confirm = () => false;
    fill(arity, '2');
    assert(arity.value === '5' && inputData(0).predicates.find(([name]) => name === 'R')[1] === 5
      && inputData(0).relations.R.every((args) => args.length === 5), 'Cancelar una reducción conserva aridad y argumentos');
    window.confirm = () => true;
    fill(arity, '2');
    assert(inputData(0).relations.R.every((args, index) => JSON.stringify(args) === JSON.stringify(original[index])),
      'Confirmar la reducción elimina solo los componentes sobrantes');
    fill(arity, '999');
    assert(inputData(0).relations.R.every((args) => args.length === 2), 'Una aridad fuera del límite no genera cientos de controles');
    load('funcion');
    const outputs = inputData(0).function_rows.f.map((entry) => entry[1]);
    fill(symbolRow('f').querySelector('input[type=number]'), '3');
    rows = inputData(0).function_rows.f;
    assert(rows.every(([args, output], index) => args.length === 3 && args[2] === '' && output === outputs[index]),
      'Cambiar la aridad de una función conserva sus salidas y añade un argumento vacío');
    fill(symbolRow('f').querySelector('input[type=number]'), '0');
    assert(inputData(0).function_rows.f.every(([args, output], index) => !args.length && output === outputs[index]),
      'La reducción a aridad cero conserva las salidas para su validación');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
