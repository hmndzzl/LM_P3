(() => {
  const background = document.getElementById('math-background');
  const symbol = background.firstElementChild;
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
    checks.push(message);
  };
  assert(background.children.length === 60 && background.getAttribute('aria-hidden') === 'true',
    'Los símbolos decorativos quedan fuera del árbol accesible');
  assert(getComputedStyle(background).pointerEvents === 'none', 'El fondo no intercepta controles');
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    assert(getComputedStyle(symbol).animationName === 'none',
      'La preferencia de movimiento reducido desactiva la animación');
  } else {
    assert(Number.parseFloat(getComputedStyle(symbol).animationDuration) === 5, 'Movimiento medio con ciclos de cinco a ocho segundos');
  }
  return { passed: checks.length, checks };
})()
