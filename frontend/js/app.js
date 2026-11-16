import { request } from './api.js';
import { inputData, renderEnvironment, errorTarget, initializeEditors, loadExample } from './editors.js';
import { clearErrors, showErrors } from './errors.js';
import { showResult } from './evidence.js';

const $ = (id) => document.getElementById(id);
let revision = 0;
let busy = false;
let dirty = false;

function invalidate() {
  revision += 1;
  dirty = true;
  clearErrors();
  $('result').hidden = true;
  $('evidence').replaceChildren();
  $('empty-result').hidden = false;
  $('result-state').textContent = 'Cambiaste los datos. Vuelve a evaluar.';
  $('environment-note').textContent = 'Vuelve a analizar si cambiaste la fórmula o el lenguaje.';
}

async function run(evaluate) {
  if (busy) return;
  clearErrors();
  $('result').hidden = true;
  $('empty-result').hidden = false;
  const version = revision;
  busy = true;
  $('evaluate').disabled = true;
  $('analyze').disabled = true;
  document.querySelector('.result-panel').setAttribute('aria-busy', 'true');
  $('result-state').textContent = evaluate ? 'Evaluando…' : 'Analizando…';
  try {
    const data = inputData(revision);
    const analysis = await request('analyze', {
      revision: version, functions: data.functions, predicates: data.predicates, formula: data.formula,
    });
    if (version !== revision || analysis.revision !== version) return;
    renderEnvironment(analysis.free_variables);
    if (!evaluate) {
      $('result-state').textContent = 'Fórmula analizada. Aún no evaluada.';
      return;
    }
    const response = await request('evaluate', inputData(revision));
    if (version !== revision || response.revision !== version) return;
    showResult(data.formula, response.evaluation);
  } catch (error) {
    if (version === revision) showErrors(error.issues || [{ message: error.message, field: '' }], errorTarget);
  } finally {
    busy = false;
    $('evaluate').disabled = false;
    $('analyze').disabled = false;
    document.querySelector('.result-panel').setAttribute('aria-busy', 'false');
  }
}

$('workspace').addEventListener('input', invalidate);
$('workspace').addEventListener('change', (event) => {
  if (event.target.tagName === 'SELECT') invalidate();
});
$('workspace').addEventListener('submit', (event) => { event.preventDefault(); run(true); });
$('analyze').addEventListener('click', () => run(false));
initializeEditors();
$('load-example').addEventListener('click', () => {
  if (dirty && !confirm('Se reemplazarán tus datos por el ejemplo. ¿Continuar?')) return;
  invalidate();
  loadExample();
});
