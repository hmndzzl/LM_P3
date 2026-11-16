# Revisión de M3 por M2 — recorrido pendiente

## Inspección actual y alcance

En la revisión de archivos del 15 de noviembre de 2026, `frontend/` solo contiene carpetas con `.gitkeep`; `lm_p3/server/` solo contiene `__init__.py`. No hay pantalla propia, codec HTTP ni punto de arranque de la aplicación. Por ello **ninguna comprobación gráfica de esta ficha se ha ejecutado**. No hay capturas, pruebas de navegador ni aprobación de accesibilidad que registrar todavía.

M2 entrega el corpus ejecutable, sus soluciones contrastadas y esta ficha para cuando esté disponible M3. Las comprobaciones Python sí están en [la evidencia M2-04](evidencias/miembro-2-corpus.md); no sustituyen esta revisión. La rotación acordada exige que una persona real haga la revisión y registre sus observaciones.

## Preparación y caso válido

Configurar el mundo de [Red de estaciones](casos-didacticos.md), conservando el orden norte, centro, sur. Usar los nombres/aridades y todas sus tablas. Si existe carga de ejemplo, debe identificarse como ejemplo editable y requerir una acción explícita; no debe reemplazar trabajo sin permitir cancelar la pérdida.

Ejecutar Q01–Q04 desde texto introducido en el editor. Verificar testigo norte, contraejemplo sur y cobertura completa de los otros dos casos. En Q03, abrir cada x y comprobar los tres testigos distintos. Comparar C01, C02 y C03: base intacta, exactamente un dato modificado y evidencia de ambos escenarios. En C02 debe verse el nuevo testigo centro con verdad conservada.

Estado de este recorrido: **pendiente de interfaz**.

## Matriz R7 para ejecutar desde los controles

Partir de `Activa(x)` con x=centro y resultado válido, introducir cada cambio por separado y pulsar **Evaluar fórmula**. Los datos completos de cada cambio y su reparación están en `examples/red_estaciones.json`. Para cada fila, verificar resumen enfocable con enlace al control, mensaje local accionable y ausencia de valor de verdad para la entrada inválida. Corregir y evaluar otra vez; debe recuperarse el resultado de la entrada reparada sin perder trabajo ajeno al error.

| Caso | Acción gráfica | Resultado esperado | Corrección | Estado |
| --- | --- | --- | --- | --- |
| E01 | Vaciar el dominio | Error de dominio; resultado anterior deja de ser actual | Restaurar los tres elementos | Pendiente |
| E02 | Desmarcar todas las tuplas de Activa | Relación vacía; no Falso | Marcar norte y centro | Pendiente |
| E03 | Dejar sin salida relevo(sur) | Función parcial, aunque no se use en la fórmula | Elegir norte como salida | Pendiente |
| E04 | Enviar dos filas con salidas distintas para centro | Rechazo antes de construir mapas | Conservar centro→sur | Pendiente |
| E05 | Escribir `Inactiva(x)` | Símbolo no declarado localizado | Cambiar a Activa | Pendiente |
| E06 | Escribir `Enlaza(x)` | Error de aridad: espera 2 y encuentra 1 | Añadir relevo(x) como segundo argumento | Pendiente |
| E07 | Usar este en una tupla | Elemento fuera de D | Seleccionar elementos de D | Pendiente |
| E08 | Quitar la asignación de x | Solicitar entorno; no evaluar prematuramente | Elegir centro | Pendiente |
| E09 | Enviar x=este | Asignación inválida bloqueada en servidor | Elegir centro | Pendiente |
| E10 | Quitar el paréntesis final | Error sintáctico localizado, texto conservado | Reponer `)` | Pendiente |
| E11 | Quitar la tabla de relevo | Símbolo sin interpretación, aunque el formulario omita ese campo | Restaurar la tabla total | Pendiente |

Si un control solo permite entradas válidas —por ejemplo, un selector que excluya este o una tabla funcional sin filas duplicables—, registrar esa prevención y verificar además el rechazo mediante una petición al servidor de pruebas. No afirmar que se ejecutó esa petición antes de disponer de la ruta/codec reales. Usar la misma lógica de validación M2; no reproducirla en el handler.

## Editor, estados y accesibilidad

| Comprobación | Procedimiento y resultado esperado | Estado |
| --- | --- | --- |
| Botones y teclado | Insertar los siete símbolos confirmados y ambos paréntesis; conservar cursor/selección, foco y undo/redo. Los alias de teclado deben producir la misma estructura | Pendiente |
| Variables libres | Alternar S02/S03; solo S02 solicita x. La escritura incompleta conserva asignaciones recuperables | Pendiente |
| Posiciones Unicode | Escribir `Activa(𝑥) ∧ Enlaza(x)`; el error de aridad debe señalar Enlaza(x) correctamente tras convertir puntos de código a UTF-16 | Pendiente |
| Cambios de contexto | Editar lenguaje/dominio/fórmula/entorno tras evaluar: invalidar resultado y traza actuales sin borrar datos recuperables | Pendiente |
| Respuestas tardías | Si hay solicitudes asíncronas, editar mientras una está pendiente y comprobar que su revisión vieja no sobrescriba el contexto nuevo | Pendiente |
| Evidencia navegable | Seleccionar subfórmulas con teclado; mostrar asignación y evidencia de esa instancia. No etiquetar pendientes como Falso ni colapsar sin acceso la comprobación completa | Pendiente |
| Error frente a falsedad | Q02 es Falso válido; E02 es entrada inválida. Distinguirlos con texto y estado, sin depender solo del color | Pendiente |
| Teclado/lector | Orden de foco, etiquetas persistentes, nombres de símbolos y un anuncio accesible coherente de resumen/resultado | Pendiente |
| Tamaños y zoom | Revisar 320, 768, 1024 y 1440 px, zoom 200%, reflujo y scroll local de tablas/fórmulas; guardar capturas reales | Pendiente |
| Contraste y recursos | Medir combinaciones reales y revisar fuentes/símbolos sin Internet. No afirmar conformidad WCAG completa a partir de una captura | Pendiente |
| Límites/cancelación | Un exceso muestra No evaluado con causa; un botón Cancelar solo se verifica si está conectado a cancelación real | Pendiente |

Las claves JSON repetidas deben rechazarse al decodificar, antes de perderlas en un diccionario. Probar también el tamaño de petición y los controles de loopback/Host/Origin cuando exista el servidor. La revisión de M2 complementa esos controles de M3; no certifica controles ausentes.

## Ficha para cada ejecución real

- Revisor, fecha, navegador/sistema y versión del proyecto: por registrar.
- Caso/pantalla/estado y pasos exactos: por registrar.
- Resultado esperado y observado: por registrar.
- Captura o evidencia real: por registrar.
- Problema y criterio incumplido, si existe: por registrar.
- Corrección, responsable y nueva verificación: por registrar.
- Estado final y limitaciones: pendiente.

No marcar M2-04 como aceptado hasta realizar la revisión, resolver observaciones bloqueantes y completar la revisión/enseñanza humanas acordadas.
