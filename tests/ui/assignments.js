// Ejecutar con la aplicación abierta mediante agent-browser eval --stdin.
(async () => {
  const $ = (id) => document.getElementById(id);
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  const oldConfirm = window.confirm;
  window.confirm = () => true;
  try {
    $('example-select').value = 'pertenencia';
    $('load-example').click();
    const originalDomain = $('domain').value;
    const saved = $('assignment-0').value;
    assert($('environment').querySelector('label').firstChild.textContent === 'x:',
      'Las asignaciones se rotulan con dos puntos');
    $('domain').value = '';
    $('domain').dispatchEvent(new Event('change', { bubbles: true }));
    assert($('assignment-0').options.length === 1 && $('assignment-0').value === '',
      'Un dominio vacío no ofrece elementos del ejemplo anterior');
    assert($('assignment-warning-0').textContent.includes(`x: ${saved}`),
      'El valor anterior se explica como aviso y no como opción del dominio');
    $('domain').value = originalDomain;
    $('domain').dispatchEvent(new Event('change', { bubbles: true }));
    assert($('assignment-0').value === saved && !$('assignment-warning-0'),
      'Restaurar el dominio recupera la asignación que vuelve a ser válida');
    $('domain').value = 'nuevo';
    $('domain').dispatchEvent(new Event('change', { bubbles: true }));
    assert([...$('assignment-0').options].map((option) => option.value).join(',') === ',nuevo',
      'Las opciones se generan únicamente a partir del dominio actual');
    $('assignment-0').value = 'nuevo';
    $('assignment-0').dispatchEvent(new Event('change', { bubbles: true }));
    const { inputData } = await import('/js/editors.js');
    assert(inputData(0).assignments[0][1] === 'nuevo' && !$('assignment-warning-0'),
      'Elegir un valor actual reemplaza la asignación anterior y retira su aviso');
    return { passed: checks.length, checks };
  } finally {
    window.confirm = oldConfirm;
  }
})()
