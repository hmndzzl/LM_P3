// La inserción nativa conserva el historial de deshacer del navegador.
export function initializeFormulaEditor() {
  const editor = document.getElementById('formula');
  const toolbar = document.getElementById('symbol-toolbar');
  const symbols = [
    ['¬', 'negación'], ['∧', 'conjunción'], ['∨', 'disyunción'],
    ['→', 'implicación'], ['↔', 'bicondicional'], ['∀', 'cuantificador universal'],
    ['∃', 'cuantificador existencial'], ['(', 'paréntesis de apertura'], [')', 'paréntesis de cierre'],
  ];
  for (const [symbol, name] of symbols) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = symbol;
    button.setAttribute('aria-label', `Insertar ${name}`);
    button.title = name;
    // Evita que un clic cambie la selección guardada en el editor.
    button.addEventListener('mousedown', (event) => event.preventDefault());
    button.addEventListener('click', () => {
      editor.focus();
      document.execCommand('insertText', false, symbol);
    });
    toolbar.append(button);
  }
}
