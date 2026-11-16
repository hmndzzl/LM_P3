// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const load = (id) => {
    $('example-select').value = id;
    $('load-example').click();
  };
  const expand = (button) => button.click();
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    load('funcion');
    assert($('world-title').textContent === 'Interpretación' && !document.body.innerText.includes('mundo'),
      'La interfaz utiliza interpretación y lenguaje en lugar de mundo');
    assert([...$('domain-overview').querySelectorAll('li')].map((item) => item.textContent).join('|') === 'a|b|c',
      'Cada elemento del dominio se muestra por separado');
    assert([...$('predicates-overview').querySelectorAll('tbody tr')].map((row) => row.textContent).join('|') === '(a, b)|(a, c)|(a, a)',
      'Las tuplas de P ocupan filas independientes y conservan sus componentes');
    const table = $('functions-overview').querySelector('table');
    assert([...table.querySelectorAll('th')].map((cell) => cell.textContent).join('|') === 'Argumentos|Imagen',
      'Las funciones distinguen argumentos e imagen en columnas');
    assert([...table.tBodies[0].rows[0].cells].map((cell) => cell.textContent).join('|') === '(a, a)|b',
      'Los argumentos de una función binaria permanecen agrupados como una tupla');
    const more = $('functions-overview').querySelector('.summary-more');
    assert(table.tBodies[0].rows.length === 4 && more.textContent.includes('filas restantes (5)'),
      'La vista previa indica explícitamente cuántas filas faltan');
    await expand(more);
    assert($('functions-overview').querySelectorAll('tbody tr').length === 9,
      'Desplegar permite consultar las nueve filas sin truncarlas');
    assert($('functions-overview').querySelectorAll('table').length === 1
      && table.querySelectorAll('caption').length === 1 && table.querySelectorAll('thead').length === 1,
      'Todas las filas pertenecen a una sola tabla sin repetir el símbolo ni los encabezados');
    more.click();
    assert([...table.tBodies[0].rows].filter((row) => !row.hidden).length === 4
      && more.getAttribute('aria-expanded') === 'false', 'Plegar oculta las filas adicionales dentro de la misma tabla');
    more.click();
    assert(table.tBodies[0].rows.length === 9 && [...table.tBodies[0].rows].every((row) => !row.hidden),
      'Volver a desplegar conserva el orden sin duplicar filas');
    const output = document.querySelector('[id^="output-"]');
    output.value = 'c';
    output.dispatchEvent(new Event('input', { bubbles: true }));
    assert($('functions-overview').querySelector('tbody tr').cells[1].textContent === 'c',
      'El resumen refleja las ediciones de la interpretación');
    load('constante');
    assert($('functions-overview').querySelector('caption').textContent === 'i · constante'
      && $('functions-overview').querySelector('tbody tr').cells[0].textContent === '()',
      'Una constante conserva su identificación y su tupla de aridad cero');
    $('domain').value = 'a\nb\nc\nd\ne\nf';
    $('domain').dispatchEvent(new Event('input', { bubbles: true }));
    const domainMore = $('domain-overview').querySelector('.summary-more');
    await expand(domainMore);
    assert($('domain-overview').querySelectorAll('li').length === 6,
      'Los elementos adicionales del dominio también se pueden consultar');
    $('clear-example').click();
    assert($('domain-overview').textContent === 'Dominio sin definir.'
      && !$('functions-overview').querySelector('table'), 'Limpiar retira las tablas del resumen');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
