const $ = (id) => document.getElementById(id);
const borradores = new Map();
let ejercicios = [];
let actual = 0;
let origenActual = "ejemplo";
let revision = 0;
let pendiente = false;

function limpiarResultado() {
  revision += 1;
  $('error').hidden = true;
  for (const campo of ['datos', 'extra']) {
    $(campo).removeAttribute('aria-invalid');
    $(`${campo}-error`).hidden = true;
  }
  $('salida').hidden = true;
  $('cargando').hidden = true;
  $('vacio').hidden = false;
  document.querySelector('.result-panel').setAttribute('aria-busy', 'false');
  $('resultado').textContent = '';
  $('estado').textContent = 'Por calcular';
  $('estado').className = 'result-state';
  $('copiar-texto').textContent = 'Copiar lista';
  $('nota-copia').hidden = true;
  $('anuncio').textContent = '';
}

function mostrarError(mensaje, campo) {
  const destino = ['datos', 'extra'].includes(campo) ? campo : 'calcular';
  $('error-enlace').textContent = mensaje;
  $('error-enlace').href = `#${destino}`;
  $('error').hidden = false;
  $('estado').textContent = 'Revisa la entrada';
  $('estado').className = 'result-state invalid';
  if (destino !== 'calcular') {
    $(destino).setAttribute('aria-invalid', 'true');
    $(`${destino}-error`).textContent = mensaje;
    $(`${destino}-error`).hidden = false;
  }
  $('error').focus();
}

function crearBorrador(numero) {
  const ejercicio = ejercicios[numero - 1];
  return {
    origen: 'ejemplo',
    ejemplo: { datos: ejercicio.datos, extra: ejercicio.extra },
    propios: { datos: ejercicio.datos, extra: ejercicio.extra },
    deshacer: null,
  };
}

function guardarEntrada() {
  if (!actual) return;
  const borrador = borradores.get(actual);
  borrador[origenActual] = { datos: $('datos').value, extra: $('extra').value };
  borrador.origen = origenActual;
}

function actualizarDeshacer() {
  $('aviso-restablecer').hidden = !borradores.get(actual).deshacer;
}

function mostrarOrigen(enfocar = false) {
  const borrador = borradores.get(actual);
  origenActual = borrador.origen;
  const ejemplo = origenActual === 'ejemplo';
  const entrada = borrador[origenActual];
  document.querySelector(`input[name="origen"][value="${origenActual}"]`).checked = true;
  $('datos').value = entrada.datos;
  $('extra').value = entrada.extra;
  $('datos').readOnly = ejemplo;
  $('extra').readOnly = ejemplo && actual === 4;
  $('nota-ejemplo').hidden = !ejemplo;
  $('modo-entrada').textContent = ejemplo ? 'Ejemplo del enunciado' : 'Datos propios';
  limpiarResultado();
  actualizarDeshacer();
  if (enfocar) $('datos').focus();
}

function cambiarOrigen() {
  if (!actual) return;
  // El radio ya cambió, pero origenActual todavía identifica lo que se editaba.
  guardarEntrada();
  const origen = document.querySelector('input[name="origen"]:checked').value;
  borradores.get(actual).origen = origen;
  mostrarOrigen(origen === 'propios');
}

function seleccionar(numero) {
  if (!ejercicios.length) return;
  guardarEntrada();
  actual = numero;
  if (!borradores.has(numero)) borradores.set(numero, crearBorrador(numero));
  const ejercicio = ejercicios[numero - 1];
  $('titulo').textContent = ejercicio.titulo;
  $('descripcion').textContent = ejercicio.descripcion;
  $('datos-etiqueta').textContent = ejercicio.etiqueta;
  $('datos-ayuda').textContent = ejercicio.ayuda;
  $('extra-grupo').hidden = !ejercicio.extra_etiqueta;
  $('extra-etiqueta').textContent = ejercicio.extra_etiqueta;
  $('extra-ayuda').textContent = ejercicio.extra_ayuda;
  $('extra').inputMode = numero === 2 ? 'numeric' : 'text';
  document.querySelectorAll('[data-ejercicio]').forEach((boton) => {
    const activo = Number(boton.dataset.ejercicio) === numero;
    boton.classList.toggle('active', activo);
    if (activo) boton.setAttribute('aria-current', 'page');
    else boton.removeAttribute('aria-current');
  });
  mostrarOrigen();
}

function restablecerEjemplo() {
  if (!actual) return;
  guardarEntrada();
  const borrador = borradores.get(actual);
  // Repetir el restablecimiento no debe borrar el punto de recuperación.
  const anterior = borrador.deshacer || {
    origen: borrador.origen,
    ejemplo: { ...borrador.ejemplo },
    propios: { ...borrador.propios },
  };
  const nuevo = crearBorrador(actual);
  nuevo.deshacer = anterior;
  borradores.set(actual, nuevo);
  mostrarOrigen();
  $('anuncio').textContent = 'Se cargó el ejemplo. Puedes deshacer el restablecimiento.';
}

function deshacerRestablecimiento() {
  if (!actual) return;
  const anterior = borradores.get(actual).deshacer;
  if (!anterior) return;
  borradores.set(actual, { ...anterior, deshacer: null });
  mostrarOrigen(true);
  $('anuncio').textContent = 'Restablecimiento deshecho. Se recuperaron tus entradas anteriores.';
}

function editarEntrada() {
  if (!actual) return;
  guardarEntrada();
  // Una edición nueva inicia otro trabajo y deja atrás el restablecimiento.
  borradores.get(actual).deshacer = null;
  actualizarDeshacer();
  limpiarResultado();
}

$('formulario').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  if (pendiente || !actual) return;
  limpiarResultado();
  if (actual === 2 && !/^\+?\d+$/.test($('extra').value.trim())) {
    mostrarError('El exponente n debe ser un número entero positivo, mayor que 0.', 'extra');
    return;
  }
  const version = revision;
  pendiente = true;
  $('calcular').disabled = true;
  $('calcular-texto').textContent = 'Calculando…';
  $('estado').textContent = 'Calculando';
  $('vacio').hidden = true;
  $('cargando').hidden = false;
  document.querySelector('.result-panel').setAttribute('aria-busy', 'true');
  try {
    const respuesta = await fetch('/api/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ejercicio: actual, datos: $('datos').value, extra: $('extra').value }),
    });
    const contenido = await respuesta.json();
    if (version !== revision) return;
    if (!respuesta.ok) {
      const error = new Error(contenido.error || 'No se pudo calcular el resultado.');
      error.campo = contenido.campo;
      throw error;
    }
    $('resultado').textContent = contenido.resultado;
    const unidad = actual === 3 ? ['fila', 'filas'] : ['elemento', 'elementos'];
    $('cantidad').textContent = `${contenido.cantidad} ${unidad[contenido.cantidad === 1 ? 0 : 1]}`;
    $('salida').hidden = false;
    $('estado').textContent = 'Calculado';
    $('estado').className = 'result-state success';
    $('anuncio').textContent = `Resultado calculado: ${contenido.resultado}`;
    if (window.matchMedia('(max-width: 880px)').matches) {
      $('resultado').focus();
    }
  } catch (error) {
    if (version !== revision) return;
    $('vacio').hidden = false;
    mostrarError(error instanceof TypeError
      ? 'No se pudo conectar. Vuelve a abrir el laboratorio desde el acceso de tu equipo.'
      : error.message, error.campo);
  } finally {
    pendiente = false;
    $('calcular').disabled = false;
    $('calcular-texto').textContent = 'Calcular resultado';
    if (version === revision) {
      $('cargando').hidden = true;
      document.querySelector('.result-panel').setAttribute('aria-busy', 'false');
    }
  }
});

$('formulario').addEventListener('keydown', (evento) => {
  if ((evento.ctrlKey || evento.metaKey) && evento.key === 'Enter') {
    evento.preventDefault();
    $('formulario').requestSubmit();
  }
});
$('error-enlace').addEventListener('click', (evento) => {
  evento.preventDefault();
  const destino = $('error-enlace').getAttribute('href').slice(1);
  $(destino).focus();
});
$('restablecer').addEventListener('click', restablecerEjemplo);
$('deshacer').addEventListener('click', deshacerRestablecimiento);
$('datos').addEventListener('input', editarEntrada);
$('extra').addEventListener('input', editarEntrada);
document.querySelectorAll('input[name="origen"]').forEach((radio) => radio.addEventListener('change', () => cambiarOrigen()));
document.querySelectorAll('[data-ejercicio]').forEach((boton) => {
  boton.addEventListener('click', () => seleccionar(Number(boton.dataset.ejercicio)));
});
$('copiar').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText($('resultado').textContent);
    $('copiar-texto').textContent = 'Lista copiada';
    $('anuncio').textContent = 'Resultado copiado al portapapeles.';
  } catch {
    const rango = document.createRange();
    rango.selectNodeContents($('resultado'));
    const seleccion = window.getSelection();
    seleccion.removeAllRanges();
    seleccion.addRange(rango);
    $('resultado').focus();
    $('nota-copia').textContent = 'El texto está seleccionado. Usa Ctrl+C o Cmd+C para copiarlo.';
    $('nota-copia').hidden = false;
  }
});

if (/Mac|iPhone|iPad/.test(navigator.platform)) $('atajo').textContent = '⌘ + Enter';
$('calcular').disabled = true;
fetch('/api/ejercicios').then((respuesta) => {
  if (!respuesta.ok) throw new Error('No se pudieron cargar los ejercicios.');
  return respuesta.json();
}).then((datos) => {
  ejercicios = datos;
  seleccionar(1);
  $('calcular').disabled = false;
}).catch(() => {
  mostrarError('No se pudo cargar el laboratorio. Cierra esta pestaña y vuelve a abrir la interfaz.');
});
