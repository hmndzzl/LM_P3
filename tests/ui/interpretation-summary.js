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
  const expand = async (details) => {
    details.open = true;
    const deadline = Date.now() + 3000;
    while (!details.dataset.loaded) {
      if (Date.now() > deadline) throw new Error('No se desplegaron las filas restantes.');
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
  };
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
    const more = $('functions-overview').querySelector('details');
    assert(table.tBodies[0].rows.length === 4 && more.firstElementChild.textContent.includes('filas restantes (5)'),
      'La vista previa indica explícitamente cuántas filas faltan');
    await expand(more);
    assert($('functions-overview').querySelectorAll('tbody tr').length === 9,
      'Desplegar permite consultar las nueve filas sin truncarlas');
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
    const domainMore = $('domain-overview').querySelector('details');
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
