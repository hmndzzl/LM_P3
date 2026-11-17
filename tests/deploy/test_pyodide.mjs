// Ejecuta los ejemplos reales con el mismo Python WebAssembly que usará Pages.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';
import { examples } from '../../frontend/js/examples.js';

const modulePath = process.env.PYODIDE_MODULE_PATH;
if (!modulePath) throw new Error('Define PYODIDE_MODULE_PATH con la ruta a pyodide.mjs instalado para la prueba.');
try {
  const { loadPyodide } = await import(pathToFileURL(resolve(modulePath)).href);
  const python = await loadPyodide({ indexURL: `${dirname(resolve(modulePath))}/` });
  await python.unpackArchive(new Uint8Array(await readFile('_site/python/lm_p3.zip')), 'zip');
  const bridge = python.pyimport('lm_p3.server.browser');
  const execute = (operation, data) => JSON.parse(bridge.execute(operation, JSON.stringify(data)));
  const expected = [true, false, true, true, true, false, true, true, false, false, true];
  assert.equal(examples.length, expected.length);
  for (const [index, example] of examples.entries()) {
    const data = { ...example.data, revision: index };
    const analysis = execute('analyze', {
      revision: index, functions: data.functions, predicates: data.predicates, formula: data.formula,
    });
    assert.equal(analysis.status, 'analyzed', JSON.stringify(analysis));
    const result = execute('evaluate', data);
    assert.equal(result.status, 'evaluated', JSON.stringify(result));
    assert.equal(result.evaluation.value, expected[index], example.id);
    assert.equal(result.revision, index);
  }
  const base = { ...structuredClone(examples[0].data), revision: 20 };
  const variant = structuredClone(base);
  variant.assignments = [['x', '3']];
  const comparison = execute('compare', { revision: 21, base, variant });
  assert.equal(comparison.status, 'compared');
  assert.equal(comparison.comparison.truth_changed, true);
  const invalid = execute('evaluate', { ...base, formula: 'P(x' });
  assert.equal(invalid.status, 'invalid');
  assert.equal(invalid.evaluation, undefined);
  const missing = execute('evaluate', { ...base, assignments: [] });
  assert.equal(missing.status, 'invalid');
  const empty = execute('evaluate', { ...base, relations: { ...base.relations, P: [] } });
  assert.equal(empty.status, 'invalid');
  bridge.destroy();
  console.log(`Pyodide ${python.version}: ${examples.length} ejemplos, análisis, comparación y rechazos verificados.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
