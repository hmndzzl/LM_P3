import { pyodideIndexURL } from './runtime-config.js';

let ready;
async function initialize() {
  const { loadPyodide } = await import(`${pyodideIndexURL}pyodide.mjs`);
  const python = await loadPyodide({ indexURL: pyodideIndexURL });
  const response = await fetch(new URL('../python/lm_p3.zip', import.meta.url));
  if (!response.ok) throw new Error('No se pudo descargar el motor del proyecto.');
  await python.unpackArchive(await response.arrayBuffer(), 'zip');
  const bridge = python.pyimport('lm_p3.server.browser');
  return { python, bridge };
}

// Las peticiones comparten la carga del intérprete, pero cada una tiene su contexto propio.
self.onmessage = async ({ data: { id, operation, payload } }) => {
  try {
    ready ||= initialize().catch((error) => { ready = undefined; throw error; });
    const { bridge } = await ready;
    const body = bridge.execute(operation, payload);
    self.postMessage({ id, body: JSON.parse(body) });
  } catch {
    self.postMessage({ id, error: 'No se pudo iniciar Python en el navegador. Comprueba tu conexión y vuelve a intentar.' });
  }
};
