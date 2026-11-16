// Fondo decorativo independiente de la evaluación y de sus datos.
export function initializeBackground() {
  const background = document.getElementById('math-background');
  const symbols = ['∀', '∃', '¬', '∧', '∨', '→', '↔', '⊨', '∈', 'α', 'β', 'γ', 'δ', 'λ', 'π', 'Σ', 'x', 'y'];
  for (let index = 0; index < 60; index += 1) {
    const symbol = document.createElement('span');
    symbol.dataset.symbol = symbols[index % symbols.length];
    symbol.style.left = `${(index * 37 + 5) % 100}%`;
    symbol.style.top = `${(index * 23 + 8) % 100}%`;
    symbol.style.fontSize = `${28 + (index % 4) * 8}px`;
    symbol.style.animationDelay = `${-index * 1.3}s`;
    symbol.style.animationDuration = `${5 + index % 4}s`;
    background.append(symbol);
  }
}
