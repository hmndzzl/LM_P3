// Fondo decorativo independiente de la evaluación y de sus datos.
export function initializeBackground() {
  const background = document.getElementById('math-background');
  const toggle = document.getElementById('background-motion');
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const symbols = ['∀', '∃', '¬', '∧', '∨', '→', '↔', '⊨', '∈'];
  for (let index = 0; index < 36; index += 1) {
    const symbol = document.createElement('span');
    symbol.dataset.symbol = symbols[index % symbols.length];
    symbol.style.left = `${(index * 37 + 5) % 100}%`;
    symbol.style.top = `${(index * 23 + 8) % 100}%`;
    symbol.style.fontSize = `${28 + (index % 4) * 8}px`;
    symbol.style.animationDelay = `${-index * 1.3}s`;
    symbol.style.animationDuration = `${5 + index % 4}s`;
    background.append(symbol);
  }
  function applyPreference() {
    toggle.disabled = preference.matches;
    toggle.setAttribute('aria-pressed', String(!preference.matches));
    background.classList.toggle('paused', preference.matches);
    toggle.title = preference.matches ? 'Movimiento desactivado por tu preferencia de accesibilidad' : 'Activar o pausar el movimiento del fondo';
  }
  toggle.addEventListener('click', () => {
    const paused = background.classList.toggle('paused');
    toggle.setAttribute('aria-pressed', String(!paused));
  });
  preference.addEventListener('change', applyPreference);
  applyPreference();
}
