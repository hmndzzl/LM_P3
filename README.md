# LM_P3 — Evaluador semántico

Proyecto de MM3032 Lógica Matemática: aplicación gráfica para evaluar fórmulas sobre interpretaciones finitas y explicar sus resultados.

## Estado actual

Se prepararon lineamientos, reparto, estructura común de carpetas y bases heredadas **sin adaptar**. Aún no existe una aplicación propia ejecutable. El arranque previsto es `python -m lm_p3`, pendiente de implementar por M3. Las pruebas propias se descubrirán con `python -m unittest discover -s tests -t . -v`; por ahora hay 0 pruebas y eso no acredita cobertura. Los archivos de `bases/` no equivalen a requisitos cumplidos.

## Documentos para comenzar

- [Estructura común](docs/estructura.md): rutas, responsabilidades, dependencias y comandos.
- [Contratos entre módulos](docs/contratos.md): fronteras definidas y acuerdos exactos pendientes de H0.

- [Bases transferidas](bases/README.md) y [manifiesto de integridad](bases/MANIFEST.json).

## Base técnica elegida

Python con servidor HTTP local y HTML/CSS/JavaScript en el navegador, comunicados mediante JSON. Se reutiliza el patrón técnico de TDLC_LAB12; el diseño visual del producto seguirá DESIGN.md. Los fragmentos de proyectos anteriores sirven como referencias seleccionadas para sintaxis y árboles.

Cada miembro hará las adaptaciones de su parte en las rutas de `docs/estructura.md`, fuera de `bases/`, después de cerrar contratos en H0. La copia completa del laboratorio conserva su funcionamiento previo; consultar su inventario para distinguir pruebas/comandos del laboratorio de los futuros del evaluador.
