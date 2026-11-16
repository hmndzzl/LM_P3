export async function request(operation, data) {
  let response;
  try {
    response = await fetch(`/api/${operation}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  } catch {
    throw new Error('No se pudo conectar. Comprueba que el servidor local siga abierto.');
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error('El servidor devolvió una respuesta ilegible. Reintenta la operación.');
  }
  if (!response.ok) {
    const error = new Error('La operación no pudo completarse.');
    error.issues = body.errors;
    throw error;
  }
  return body;
}
