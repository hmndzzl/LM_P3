import { request } from './api.js';
import {
  inputData, renderEnvironment, errorTarget, initializeEditors, loadExample, clearEditors, updateWorldSummary,
} from './editors.js';
import { clearErrors, showErrors } from './errors.js';
import { showResult } from './evidence.js';
import { initializeFormulaEditor } from './formula.js';
import { clearComparison, setComparisonBase, initializeComparison } from './comparison.js';
import { initializeBackground } from './background.js';
import { examples } from './examples.js';

const $ = (id) => document.getElementById(id);
let revision = 0;
let busy = false;
let dirty = false;

function invalidate(event) {
  revision += 1;
  dirty = true;
  clearErrors();
  clearComparison();
  $('result').hidden = true;
  $('evidence').replaceChildren();
  $('empty-result').hidden = false;
  $('result-state').textContent = 'Cambiaste los datos. Vuelve a evaluar.';
  updateWorldSummary();
  if (!event?.target.closest('#environment')) {
    $('environment-note').textContent = 'Si cambiaste la fórmula o el lenguaje, revisa las variables libres.';
    $('example-note').hidden = true;
    $('start-description').hidden = false;
  }
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
    const evaluatedData = inputData(revision);
    const response = await request('evaluate', evaluatedData);
    if (version !== revision || response.revision !== version) return;
    showResult(data.formula, response.evaluation);
    setComparisonBase(evaluatedData);
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
  if (event.target.tagName === 'SELECT') invalidate(event);
});
$('workspace').addEventListener('submit', (event) => { event.preventDefault(); run(true); });
$('analyze').addEventListener('click', () => run(false));
initializeEditors();
initializeFormulaEditor();
initializeComparison();
initializeBackground();
for (const example of examples) $('example-select').append(new Option(example.title, example.id));

$('load-example').addEventListener('click', () => {
  if (dirty && !confirm('Se reemplazarán tus datos por el ejemplo. ¿Continuar?')) return;
  invalidate();
  loadExample(examples.find((example) => example.id === $('example-select').value));
});
$('clear-example').addEventListener('click', () => {
  if (dirty && !confirm('Se borrarán fórmula, lenguaje, dominio, tablas, asignaciones y resultados. ¿Continuar?')) return;
  invalidate();
  clearEditors();
  dirty = false;
  $('result-formula').replaceChildren();
  $('result-value').textContent = '';
  $('result-value').removeAttribute('data-value');
  $('result-reason').textContent = '';
  $('evidence-selection').textContent = '';
  $('result-state').textContent = 'Sin evaluar';
  $('formula').focus();
});
