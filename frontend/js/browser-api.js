let worker;
let sequence = 0;
const pending = new Map();
const TIMEOUT = 120_000;

function stop(error) {
  worker?.terminate();
  worker = undefined;
  for (const { reject, timer } of pending.values()) {
    clearTimeout(timer);
    reject(error);
  }
  pending.clear();
}

function getWorker() {
  if (worker) return worker;
  worker = new Worker(new URL('./python-worker.js', import.meta.url), { type: 'module' });
  worker.onmessage = ({ data }) => {
    const request = pending.get(data.id);
    if (!request) return;
    clearTimeout(request.timer);
    pending.delete(data.id);
    if (data.error) request.reject(new Error(data.error));
    else request.resolve(data.body);
  };
  worker.onerror = () => stop(new Error('No se pudo cargar el motor. Comprueba tu conexión y vuelve a intentar.'));
  worker.onmessageerror = () => stop(new Error('No se pudo leer la respuesta del motor. Vuelve a intentar.'));
  return worker;
}

export function browserRequest(operation, data) {
  return new Promise((resolve, reject) => {
    const active = getWorker();
    const id = ++sequence;
    const timer = setTimeout(() => stop(new Error('La operación tardó demasiado. Reduce los datos y vuelve a intentar.')), TIMEOUT);
    pending.set(id, { resolve, reject, timer });
    try {
      active.postMessage({ id, operation, payload: JSON.stringify(data) });
    } catch (error) {
      clearTimeout(timer);
      pending.delete(id);
      reject(error);
    }
  });
}
