# El artefacto público incluye solo interfaz y código del evaluador.
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from scripts.build_pages import build


class PagesBuildTests(unittest.TestCase):
    def test_build_uses_relative_assets_and_the_python_engine_without_private_files(self):
        with TemporaryDirectory() as temp:
            output = Path(temp) / 'site'
            build(output)
            html = (output / 'index.html').read_text()
            self.assertIn('./css/styles.css', html)
            self.assertNotIn('src="/js/', html)
            self.assertIn("executionMode = 'browser'", (output / 'js/runtime-config.js').read_text())
            self.assertTrue((output / '.nojekyll').is_file())
            with ZipFile(output / 'python/lm_p3.zip') as archive:
                names = archive.namelist()
                self.assertIn('lm_p3/semantics/evaluator.py', names)
                self.assertIn('lm_p3/server/browser.py', names)
                self.assertIn('lm_p3/syntax/parser.py', names)
                self.assertNotIn('lm_p3/server/http.py', names)
                self.assertNotIn('lm_p3/__main__.py', names)
                self.assertTrue(all(name.startswith('lm_p3/') and name.endswith('.py') for name in names))
            self.assertFalse((output / 'tasks').exists())
            self.assertFalse((output / 'bases').exists())
            self.assertFalse((output / 'AGENTS.md').exists())
            self.assertIn('sha256', json.loads((output / 'build-info.json').read_text()))

    def test_python_archive_is_reproducible(self):
        with TemporaryDirectory() as temp:
            first, second = Path(temp) / 'first', Path(temp) / 'second'
            build(first)
            build(second)
            self.assertEqual((first / 'python/lm_p3.zip').read_bytes(), (second / 'python/lm_p3.zip').read_bytes())

    def test_existing_content_is_never_overwritten(self):
        with TemporaryDirectory() as temp:
            output = Path(temp)
            (output / 'keep.txt').write_text('contenido ajeno')
            with self.assertRaises(FileExistsError):
                build(output)
            self.assertEqual((output / 'keep.txt').read_text(), 'contenido ajeno')


if __name__ == '__main__':
    unittest.main()
