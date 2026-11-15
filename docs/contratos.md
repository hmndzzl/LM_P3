# Contratos comunes entre miembros

## Estado

Documento inicial de coordinación asociado a [estructura.md](estructura.md). Las responsabilidades y dirección de dependencias están definidas. **Las firmas exactas, modelos y el esquema JSON todavía deben cerrarse entre los tres en H0**, antes de implementar consumidores. Esto no introduce clases ni endpoints funcionales y no confirma notación pendiente del curso.

## Fronteras y responsables

| Frontera | Proveedor | Consumidor | Qué acordar y probar |
| --- | --- | --- | --- |
| Lenguaje/interpretación | M2 en `models/language.py` | M1, M2, codec de M3 | Nombres y aridades, orden estable de D, tablas totales y relaciones no vacías |
| Análisis de fórmula | M2 en `syntax/` | Servicio/M1 y UI a través del servidor | AST, variables libres, posiciones, error sintáctico; preservar lexemas |
| Entrada validada | M2 en `validation/` | M1 en `semantics/` | Marca/tipo de entrada válida, entorno completo y ausencia de errores |
| Evaluación/traza | M1 en `semantics/` y `models/trace.py` | Servicio y codec/UI de M3 | Booleano, entorno, subfórmula, motivo, hijos, cobertura, visitado y evidencia decisiva |
| Caso de uso completo | M1 en `application/service.py`, junto a M2 | Servidor M3 | Analizar, validar y luego evaluar, sin valor de verdad en fallos |
| JSON/HTTP | M3 en `server/codec.py` y `server/http.py` | Frontend M3; pruebas cruzadas | Forma de petición, rutas, códigos de error y versión de contexto; sin modelos arbitrarios expuestos |
| Comparación P1 | M1 en `semantics/comparison.py` | Servicio y UI M3 | Base inmutable, variante de un cambio válido y evidencia de ambas |

## Reglas ya fijadas

1. La petición lleva lenguaje, interpretación, texto de fórmula, entorno y revisión del contexto; el servidor devuelve esa revisión para que la UI descarte respuestas obsoletas. No aceptar AST/traza aportados por el navegador como evidencia calculada.
2. El resultado válido contiene un booleano y una traza estructurada. Entradas inválidas, error interno y límites no incluyen un booleano que la UI pueda confundir con verdad. Un resultado Falso válido no es error HTTP.
3. Usar una estructura consistente de errores con código estable, mensaje en español y campo/rango cuando corresponda. La UI no deduce tipos de error analizando texto libre. Rechazar errores de JSON/tipos en frontera y errores lógicos mediante validación integral.
4. El análisis debe permitir pedir asignaciones de variables libres antes de evaluar. Acordar si hay una operación separada de análisis o respuesta intermedia; no exigir a M3 un parser completo en JavaScript.
5. Las funciones internas reciben modelos compartidos; el codec es el único traductor de JSON. El servidor no importa una interfaz CLI ni funciones de ejercicios previos. No devolver HTML desde el motor.
6. Para un existencial falso/universal verdadero, la evidencia debe conservar comprobación de cada elemento. Paginación/colapso de UI no reduce esa obligación. No presentar el orden de recorrido como razón lógica.
7. Versionar la edición no implica almacenar sesiones en el servidor: preferir peticiones autocontenidas y evitar estado global mutable. El entero de revisión no es control de seguridad ni un valor de verdad.

## Pendientes de H0 (no asumir resueltos)

- [ ] Catálogo del curso, precedencia, asociatividad, alcance, igualdad y aridad cero.
- [ ] Tipos exactos y representación de términos, átomos, conectivos y cuantificadores; ubicaciones consistentes entre Python y JS, incluyendo índices Unicode/UTF-16.
- [ ] Representación JSON de D, funciones, relaciones y entorno; nombres exactos y política de duplicados. Debe representar tuplas n-arias sin codificaciones ambiguas.
- [ ] Firmas públicas del parser, analizador de variables libres, validador, evaluador, comparación y servicio; estrategia única de errores esperados.
- [ ] Operaciones/rutas HTTP mínimas para análisis, evaluación y comparación; códigos de estado, forma uniforme de respuestas y límites de recursos. No agregar CRUD ni almacenamiento que el proyecto no necesita.
- [ ] Campos de traza, identificadores de subfórmula, cobertura y relación con posiciones del editor; serialización estable y suficiente para el explorador.
- [ ] Casos JSON completos: válido verdadero, válido falso, fórmula abierta con entorno pendiente, error de sintaxis, interpretación inválida y cambio de comparación. Convertirlos luego en fixtures de prueba revisadas por proveedor y consumidor.
- [ ] Versión concreta de Python y navegadores usados por el grupo; comandos de arranque/pruebas comprobados cuando exista la implementación.

Cada pendiente debe cerrarse editando este archivo con la decisión y ejemplos concretos, no marcando solamente una casilla. Ningún agente inventará contratos diferentes en su módulo para avanzar sin coordinar. Los modelos quedan bajo responsables de estructura.md y cualquier cambio se revisa con sus consumidores.
