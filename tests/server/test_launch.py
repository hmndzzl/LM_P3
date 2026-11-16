from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class LaunchTests(unittest.TestCase):
    def test_module_documents_its_launch_options(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'lm_p3', '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--no-browser', result.stdout)

    @unittest.skipIf(sys.platform == 'win32', 'El lanzador POSIX se prueba en Linux/macOS.')
    def test_posix_launchers_resolve_the_root_from_another_directory(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            for name in ('abrir_interfaz.sh', 'abrir_interfaz.command'):
                with self.subTest(name=name):
                    result = subprocess.run(['sh', str(root / 'scripts' / name), '--help'],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('--port', result.stdout)
