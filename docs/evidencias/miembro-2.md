# Evidencia de implementación — Miembro 2

## Alcance y entorno

Fecha: 15 de noviembre de 2026. Rama existente preparada por el usuario: `feature/sintaxis-validacion`. Intérprete usado: `C:\UVG\logica\LM_P3\.venv\Scripts\python.exe`, Python 3.11.9, Windows. No se instalaron dependencias ni se hicieron staging, commits, push o cambios de rama.

Se implementaron lexer/parser de términos y fórmulas, análisis de variables libres, validación de declaraciones de lenguaje y errores sintácticos localizados. Se reutilizan los modelos y el servicio de M1. Los operadores del AST son canónicos aunque el texto contenga alias. Las pruebas nuevas de integración usan el parser real; no adaptadores que devuelvan AST prefijados.

## Comprobaciones ejecutadas

Desde `C:\UVG\logica\LM_P3`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -t .
.\.venv\Scripts\python.exe -X utf8 -B -m examples.sintaxis
git diff --check
git diff --name-only -- bases
```

| Comprobación | Resultado observado |
| --- | --- |
| Suite propia completa | 79 pruebas pasan, sin omisiones; incluye las 44 pruebas previas de M1 y su oráculo de 900 evaluaciones |
| Árboles manuales | Términos anidados, argumentos múltiples, conectivos y cuantificadores producen el AST esperado |
| Notación | Los siete símbolos oficiales y cada alias producen operadores canónicos; `<->` se reconoce completo antes de `->` |
| Precedencia/asociatividad | Todos los niveles, implicación a la derecha, otros binarios a la izquierda y paréntesis explícitos |
| Alcance | Cuantificador mínimo frente a cuerpo parentizado, anidamiento, sombra y ocurrencias libres fuera del cuantificador |
| Nombres y aridades | Nombres personalizados/Unicode, colisiones de alias, funciones/predicados cero-arios y rechazo de nombres/aridades inválidos |
| Posiciones | Rangos originales incluso con alias, texto multilínea, fin de entrada y variable 𝑥 fuera del plano básico |
| Error sintáctico | Símbolos desconocidos, funciones/predicados en posición incorrecta, argumentos, delimitadores, operandos y texto sobrante; errores sin atributo `value` |
| Límites | Excesos de texto/tokens, paréntesis, prefijos, términos y profundidad de AST fallan sin verdad; una nueva ejecución sigue funcionando |
| Texto → motor real | Átomo abierto, funciones anidadas, cuatro casos cuantificados, restauración del entorno y rechazo de interpretación parcial aunque no se use f |
| Independencia de ejemplos | Lenguaje personalizado y dominio de tres elementos; testigo calculado `persona=dos` |
| Aridad cero e igualdad declarada | `T() ↔ P(c)`, `∀x Igual(x,x)` y `∃x Igual(x,c())` se evalúan sobre interpretaciones explícitas |
| Fixtures compartidas | Seis casos JSON con resultados manuales coinciden con análisis y motor reales; no fijan el esquema HTTP |
| Demo | Resultados Verdadero, Falso, Verdadero, Falso, Falso; ejemplo de aridad inválida sin verdad |
| Diff | `git diff --check` sin errores; `git diff --name-only -- bases` sin salida |

En esta consola los símbolos lógicos requieren `-X utf8`; el entorno no necesita paquetes externos. Solo se ejecutó esta entrega de M2 con Python 3.11.9; no se afirma haberla probado en 3.10, 3.14 ni otro sistema operativo.

## Estado de aceptación y próximos pasos

- M2-01/02 tienen implementación y evidencia Python. Pendientes: revisión humana de M1 y recorrido real con interfaz de M3; no se marcan como globalmente aceptados.
- M2-03 sigue pendiente. `validate_language` cubre declaraciones; `prepare_input` de M1 certifica modelos normalizados. Esto no reemplaza validar entradas externas ni detectar duplicados contradictorios antes de construir mapas. Se debe acordar ese camino con el codec de M3 y conectar el validador integral al servicio.
- M2-04 sigue pendiente: corpus didáctico completo, revisión de M3, enseñanza entre integrantes y defensa. Las fixtures actuales no acreditan estas actividades humanas.
- M3 debe exponer `analyze` para pedir el entorno, convertir rangos a UTF-16, presentar errores/trazas y descartar respuestas de revisiones anteriores. No se creó servidor ni interfaz.
- Contrato de análisis actualizado en `docs/contratos.md`; gramática y convenciones en `docs/sintaxis.md`. M1/M3 deben revisar estos archivos; no se enviaron mensajes externos en su nombre.
- Se actualizaron también `plan.md`, `todo.md` y la guía de M2 en `C:\UVG\logica`. En esta copia esos archivos están fuera del repositorio `LM_P3`, por lo que no aparecen en su `git diff`; no se movieron ni duplicaron automáticamente.
