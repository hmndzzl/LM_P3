# Genera el sitio estático sin incluir repositorio, instrucciones locales ni bases heredadas.
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'lm_p3/server/http.py', 'lm_p3/__main__.py'}


def build(output: Path) -> None:
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('El destino debe estar vacío. Elige otra carpeta de salida.')
    output.mkdir(parents=True, exist_ok=True)
    # Se seleccionan extensiones de recursos; no se copia la raíz del proyecto.
    for source in sorted((ROOT / 'frontend').rglob('*')):
        if source.is_symlink() or not source.is_file() or source.name.startswith('.'):
            continue
        if source.suffix not in {'.html', '.css', '.js', '.svg', '.png', '.webp', '.woff2', '.ico'}:
            continue
        relative = source.relative_to(ROOT / 'frontend')
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    config = output / 'js/runtime-config.js'
    config.write_text(config.read_text().replace("executionMode = 'server'", "executionMode = 'browser'"))
    (output / 'python').mkdir()
    package = output / 'python/lm_p3.zip'
    with ZipFile(package, 'w', compression=ZIP_DEFLATED) as archive:
        for source in sorted((ROOT / 'lm_p3').rglob('*.py')):
            relative = source.relative_to(ROOT).as_posix()
            if relative in EXCLUDED or source.is_symlink() or '__pycache__' in source.parts:
                continue
            entry = ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, source.read_bytes())
    (output / '.nojekyll').touch()
    (output / 'build-info.json').write_text(json.dumps({
        'engine': 'lm_p3/python', 'sha256': sha256(package.read_bytes()).hexdigest(),
        'transport': 'pyodide-worker',
    }, indent=2) + '\n')
    # El estado explica la carga inicial sin cambiar las pantallas de trabajo.
    html = output / 'index.html'
    content = html.read_text()
    marker = '<main>'
    notice = '''<main>
    <p id="runtime-status" class="notice" role="status" aria-live="polite">
      El evaluador ejecuta Python en tu navegador. La primera operación descarga el motor y puede tardar unos segundos.
    </p>'''
    html.write_text(content.replace(marker, notice, 1))


def main() -> None:
    parser = argparse.ArgumentParser(description='Preparar el evaluador para GitHub Pages.')
    parser.add_argument('--output', type=Path, default=ROOT / '_site', help='Carpeta vacía para el sitio generado.')
    args = parser.parse_args()
    build(args.output)
    print(f'Sitio preparado en {args.output.resolve()}')


if __name__ == '__main__':
    main()
