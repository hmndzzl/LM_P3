# Evidencia de implementación — Miembro 1

## Comprobaciones ejecutadas

Se trabajó sobre la rama `feat/semantica`, sin staging, commits, push ni cambios de rama. No se modificaron las copias heredadas de `bases/`, el parser, el servidor ni el frontend.

| Comprobación | Resultado observado |
| --- | --- |
| Suite propia en Python 3.11.12 | 44 pruebas, todas pasan; sin omisiones |
| Suite propia en Python 3.14 | 44 pruebas, todas pasan; sin omisiones |
| Oráculo independiente en `test_finite_oracle.py` | 900 evaluaciones correctas: 3 relaciones unarias no vacías × 15 binarias no vacías × 4 funciones unarias × 5 fórmulas |
| Tablas de verdad | Las cuatro combinaciones de operandos para ∧, ∨, → y ↔; doble negación |
| Evidencias cuantificadas | Testigo, contraejemplo y comprobaciones completas de todo D en los otros dos casos |
| Alcance y aislamiento | Sombra, anidamiento, restauración, snapshots inmutables y 12 evaluaciones concurrentes del mismo snapshot |
| Errores | AST/símbolos/aridades, dominio, tablas parciales, vacíos, tuplas, entorno y ramas no visitadas por un cuantificador decisivo |
| Comparación | Función/relación/asignación, verdad que cambia o se mantiene, nuevo testigo sin nueva verdad, rechazo de varios/cero cambios y contextos distintos |
| Límites/cancelación | Fallos antes/durante recorrido sin verdad parcial; nueva ejecución posterior sigue funcionando |
| Regresión de certificación | `dataclasses.replace` no permite sustituir la fórmula de una entrada certificada sin volver a validar |
| Servicio | Parser inyectado, error sintáctico propagado y rechazo de contexto o límites sustituidos por el validador |
| Mutación temporal | Cambiar `not left.value or right.value` por `left.value or right.value` hace fallar la tabla de implicación; se restauró el archivo original |
| Demo ejecutable y JSON | Cuatro resultados [true, false, true, false] y comparación [false, true]; salida serializable comprobada en prueba de integración |

La prueba de errores en una rama inválida usa validación completa previa; no se presenta un cortocircuito como sustituto de validar. La prueba de servicio usa un adaptador de parser explícito: no acredita análisis de texto ni una integración con M2 que todavía no existe.

## Rendimiento observado, no garantía

Comando: `python -B -m examples.semantica --benchmark`, ejecutado con Python 3.11.12 local. Fórmula ∀x∀y∀z P(x), con P=D para obligar a completar el recorrido; incluye certificación y construcción de evidencia, sin servidor ni renderizado.

| Tamaño de D | Verdad | Visitas | Tiempo observado |
| ---: | --- | ---: | ---: |
| 2 | Verdadero | 23 | 0.000065 s |
| 30 | Verdadero | 54 931 | 0.065193 s |

Son dos mediciones orientativas, no un benchmark estadístico ni un SLA. Otros árboles/interpretaciones pueden exigir mucho más trabajo y memoria. Por defecto el motor limita pasos a 100 000, profundidad a 128 y nodos de entrada a 20 000; no garantiza un tiempo máximo de pared. Una ejecución incompleta lanza una excepción sin resultado lógico.

## Reproducción

Desde la raíz y con Python compatible:

```sh
python -B -m unittest discover -s tests -t . -v
python -B -m examples.semantica
python -B -m examples.semantica --json
python -B -m examples.semantica --benchmark
```

[miembro-1-demo.json](miembro-1-demo.json) es la salida real de `--json` guardada durante la entrega; usa las clases y recorrido reales, no resultados escritos a mano. Para revisar la API y explicar el algoritmo, consultar [semantica.md](../semantica.md).

## Estado de aceptación

La implementación de términos/átomos, lógica/cuantificadores y comparación está comprobada a nivel de motor y del servicio inyectado. M1-04 tiene guía y mediciones, pero no se declaran realizadas las actividades humanas.

Pendiente: revisión del contrato por M2/M3, conexión a parser/validador externo y pantalla reales, contraste con corpus de M2 cuando exista, revisión humana, enseñanza mutua, ensayo individual y ejecución de la aplicación completa desde copia limpia. El conjunto de tickets mantiene aceptación global pendiente hasta completar esas verificaciones; no se afirma que R1–R7 funcionen desde una interfaz aún inexistente.
