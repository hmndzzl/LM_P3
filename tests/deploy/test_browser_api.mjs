// Comprueba correlación, reinicio y errores del transporte sin simular resultados lógicos.
import assert from 'node:assert/strict';
import test from 'node:test';

let serial = 0;
async function client() {
  const workers = [];
  class FakeWorker {
    constructor(url, options) {
      assert.equal(options.type, 'module');
      assert.ok(url.pathname.endsWith('/python-worker.js'));
      this.sent = [];
      workers.push(this);
    }
    postMessage(message) { this.sent.push(message); }
    terminate() { this.terminated = true; }
  }
  globalThis.Worker = FakeWorker;
  const api = await import(`../../frontend/js/browser-api.js?test=${++serial}`);
  return { ...api, workers };
}

test('Las respuestas fuera de orden resuelven solo su petición y conservan revisión', async () => {
  const { browserRequest, workers } = await client();
  const first = browserRequest('analyze', { revision: 1 });
  const second = browserRequest('evaluate', { revision: 2 });
  assert.equal(workers.length, 1);
  const [a, b] = workers[0].sent;
  assert.notEqual(a.id, b.id);
  assert.equal(JSON.parse(b.payload).revision, 2);
  workers[0].onmessage({ data: { id: b.id, body: { revision: 2 } } });
  workers[0].onmessage({ data: { id: a.id, body: { revision: 1 } } });
  assert.deepEqual(await first, { revision: 1 });
  assert.deepEqual(await second, { revision: 2 });
});

test('Un fallo de carga se propaga y la siguiente petición usa un worker nuevo', async () => {
  const { browserRequest, workers } = await client();
  const pending = browserRequest('analyze', {});
  const rejection = assert.rejects(pending, /motor/);
  workers[0].onerror();
  await rejection;
  assert.equal(workers[0].terminated, true);
  const next = browserRequest('analyze', {});
  assert.equal(workers.length, 2);
  workers[1].onmessage({ data: { id: workers[1].sent[0].id, body: { status: 'analyzed' } } });
  assert.equal((await next).status, 'analyzed');
});

test('El error del intérprete no se convierte en resultado Falso', async () => {
  const { browserRequest, workers } = await client();
  const pending = browserRequest('evaluate', {});
  const rejection = assert.rejects(pending, /iniciar/);
  workers[0].onmessage({ data: { id: workers[0].sent[0].id, error: 'No se pudo iniciar Python.' } });
  await rejection;
});
