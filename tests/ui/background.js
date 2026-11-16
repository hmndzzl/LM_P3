(() => {
  const background = document.getElementById('math-background');
  const toggle = document.getElementById('background-motion');
  const symbol = background.firstElementChild;
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  assert(background.children.length === 36 && background.getAttribute('aria-hidden') === 'true',
    'Los símbolos decorativos quedan fuera del árbol accesible');
  assert(getComputedStyle(background).pointerEvents === 'none', 'El fondo no intercepta controles');
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    assert(getComputedStyle(symbol).animationName === 'none' && toggle.disabled,
      'La preferencia de movimiento reducido desactiva la animación');
  } else {
    assert(Number.parseFloat(getComputedStyle(symbol).animationDuration) === 5, 'Movimiento medio con ciclos de cinco a ocho segundos');
    toggle.click();
    assert(getComputedStyle(symbol).animationPlayState === 'paused'
      && toggle.getAttribute('aria-pressed') === 'false', 'El botón pausa el fondo');
    toggle.click();
    assert(getComputedStyle(symbol).animationPlayState === 'running', 'El botón permite reanudarlo');
  }
  return { passed: checks.length, checks };
})()
