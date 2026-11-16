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
  const evaluate = async (formula) => {
    $('formula').value = formula;
    $('formula').dispatchEvent(new Event('input', { bubbles: true }));
    $('workspace').requestSubmit();
    await until(() => !$('evaluate').disabled);
  };
  const open = async (details) => {
    details.open = true;
    await until(() => details.dataset.loaded === 'true');
  };
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    $('example-select').value = 'relaciones';
    $('load-example').click();
    await evaluate('∀x ∀y R(x,y)');
    assert($('result-value').textContent === 'Falso', 'Se reproduce el resultado de la captura con el motor real');
    const root = $('evidence').firstElementChild;
    await open(root);
    const inner = root.querySelector('details');
    await open(inner);
    const atom = inner.querySelector('details');
    await open(atom);
    const summaries = [...$('evidence').querySelectorAll('summary')].map((summary) => summary.textContent);
    assert(summaries[0].startsWith('Paso 1 ·') && summaries[1].startsWith('Paso 1.1 ·')
      && summaries[2].startsWith('Paso 1.1.1 ·'), 'La numeración refleja la relación entre pasos exteriores e interiores');
    assert(summaries[1].includes('x: 1') && summaries[2].includes('x: 1, y: 1'),
      'Cada comprobación muestra los valores con los que se evaluó');
    assert(atom.textContent.includes('La tupla (1, 1) no pertenece a R'),
      'La consulta concreta explica el origen del resultado falso');
    assert(root.textContent.includes('Valores probados de x: 1.') && inner.textContent.includes('Valores probados de y: 1.'),
      'Los cuantificadores identifican qué valores se probaron');
    assert(inner.textContent.includes('ya se encontró un contraejemplo') && inner.textContent.includes('casos omitidos sean falsos'),
      'El corte del recorrido explica por qué se omitieron otros valores sin evaluarlos como falsos');
    assert($('evidence-selection').textContent.includes('Paso 1.1.1: R(x, y)')
      && $('evidence-selection').textContent.includes('Valores: x: 1, y: 1')
      && !$('evidence-selection').textContent.includes('@') && !$('evidence-selection').textContent.includes('Instancia'),
      'El paso seleccionado muestra su contexto en vez del identificador interno');
    assert($('result-formula').querySelector('mark').textContent === 'R(x,y)',
      'La selección conserva el resaltado de la subfórmula original');
    await evaluate('∃x P(x)');
    await open($('evidence').firstElementChild);
    assert($('result-reason').textContent.includes('basta un caso')
      && $('evidence').textContent.includes('ya se encontró un testigo'), 'El existencial explica por qué basta el testigo');
    await evaluate('∀x (P(x) ∨ ¬P(x))');
    await open($('evidence').firstElementChild);
    const children = [...$('evidence').firstElementChild.children].filter((child) => child.tagName === 'DETAILS');
    assert(children.length === 3 && children[0].firstElementChild.textContent.includes('x: 1')
      && children[1].firstElementChild.textContent.includes('x: 2') && children[2].firstElementChild.textContent.includes('x: 3'),
      'Las repeticiones de una misma subfórmula se distinguen por sus asignaciones');
    assert($('result-reason').textContent.includes('verdadera para cada valor de x'),
      'El universal completo explica que todos los casos fueron verdaderos');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
