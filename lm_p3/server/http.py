# Adapta el transporte del laboratorio TDLC_LAB12; no importa sus ejercicios.
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import webbrowser

from lm_p3.models.errors import EvaluationLimitError, SemanticInputError
from lm_p3.server.codec import decode_request, error_response, process_request

ROOT = Path(__file__).resolve().parents[2]
MAX_BODY = 256 * 1024
MAX_RESPONSE = 8 * 1024 * 1024
STATIC_FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/css/tokens.css': ('css/tokens.css', 'text/css; charset=utf-8'),
    '/css/styles.css': ('css/styles.css', 'text/css; charset=utf-8'),
    '/css/background.css': ('css/background.css', 'text/css; charset=utf-8'),
    '/js/app.js': ('js/app.js', 'text/javascript; charset=utf-8'),
    '/js/api.js': ('js/api.js', 'text/javascript; charset=utf-8'),
    '/js/runtime-config.js': ('js/runtime-config.js', 'text/javascript; charset=utf-8'),
    '/js/examples.js': ('js/examples.js', 'text/javascript; charset=utf-8'),
    '/js/editors.js': ('js/editors.js', 'text/javascript; charset=utf-8'),
    '/js/errors.js': ('js/errors.js', 'text/javascript; charset=utf-8'),
    '/js/evidence.js': ('js/evidence.js', 'text/javascript; charset=utf-8'),
    '/js/formula.js': ('js/formula.js', 'text/javascript; charset=utf-8'),
    '/js/comparison.js': ('js/comparison.js', 'text/javascript; charset=utf-8'),
    '/js/background.js': ('js/background.js', 'text/javascript; charset=utf-8'),
}


class LocalHandler(BaseHTTPRequestHandler):
    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def _send(self, status: int, body: bytes | dict, content_type: str = 'application/json; charset=utf-8') -> None:
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=True, allow_nan=False).encode('utf-8')
        if len(body) > MAX_RESPONSE:
            status = 422
            body = json.dumps(error_response(EvaluationLimitError(
                'La evidencia supera 8 MB. Reduce la fórmula o el dominio.'))).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.send_header('Connection', 'close')
        self.end_headers()
        self.close_connection = True
        self.wfile.write(body)

    def _host_valid(self) -> bool:
        return self.headers.get_all('Host') == [f'127.0.0.1:{self.server.server_port}']

    def do_GET(self) -> None:
        if not self._host_valid():
            self._send(403, error_response(SemanticInputError('invalid_host', 'Usa la dirección local indicada.')))
            return
        if self.path not in STATIC_FILES:
            self._send(404, error_response(SemanticInputError('not_found', 'Archivo no encontrado.')))
            return
        name, content_type = STATIC_FILES[self.path]
        path = ROOT / 'frontend' / name
        if not path.is_file():
            self._send(404, error_response(SemanticInputError('not_found', 'Interfaz aún no disponible.')))
            return
        self._send(200, path.read_bytes(), content_type)

    def do_POST(self) -> None:
        origin = f'http://127.0.0.1:{self.server.server_port}'
        if not self._host_valid() or self.headers.get_all('Origin') != [origin]:
            self._send(403, error_response(SemanticInputError('invalid_origin', 'Abre la aplicación desde su dirección local.')))
            return
        routes = {'/api/analyze': 'analyze', '/api/evaluate': 'evaluate', '/api/compare': 'compare'}
        if self.path not in routes:
            self._send(404, error_response(SemanticInputError('not_found', 'Operación no encontrada.')))
            return
        revision = None
        try:
            if self.headers.get_content_type() != 'application/json':
                self._send(415, error_response(SemanticInputError('invalid_content_type', 'Envía application/json.')))
                return
            lengths = self.headers.get_all('Content-Length', [])
            if self.headers.get('Transfer-Encoding') or len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
                raise SemanticInputError('invalid_length', 'Indica un único tamaño de petición válido.', 'request')
            length_text = lengths[0].lstrip('0') or '0'
            if len(length_text) > 6 or int(length_text) > MAX_BODY:
                self._send(413, error_response(EvaluationLimitError('La petición supera 256 KB. Reduce los datos.')))
                return
            length = int(length_text)
            if length == 0:
                raise SemanticInputError('empty_request', 'La petición está vacía.', 'request')
            body = self.rfile.read(length)
            if len(body) != length:
                raise SemanticInputError('incomplete_request', 'La petición llegó incompleta.', 'request')
            data = decode_request(body)
            if type(data.get('revision')) is int and data['revision'] >= 0:
                revision = data['revision']
            self._send(200, process_request(routes[self.path], data))
        except SemanticInputError as error:
            self._send(400, error_response(error, revision))
        except EvaluationLimitError as error:
            self._send(422, error_response(error, revision))
        except TimeoutError:
            self._send(408, error_response(EvaluationLimitError('La petición tardó demasiado en llegar.'), revision))
        except Exception:
            logging.exception('Fallo al procesar la petición local')
            error = RuntimeError('No se pudo completar la evaluación. Reintenta o consulta la consola.')
            self._send(500, error_response(error, revision))

    def log_message(self, format: str, *args: object) -> None:
        pass


def make_server(port: int = 0) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(('127.0.0.1', port), LocalHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description='Evaluador semántico local de MM3032.')
    parser.add_argument('--port', type=int, default=0, help='Puerto local; 0 elige uno disponible.')
    parser.add_argument('--no-browser', action='store_true', help='No abrir el navegador automáticamente.')
    args = parser.parse_args()
    with make_server(args.port) as server:
        address = f'http://127.0.0.1:{server.server_port}'
        print(f'Evaluador semántico: {address}', flush=True)
        print('Para cerrar, presiona Ctrl+C.', flush=True)
        if not args.no_browser:
            webbrowser.open(address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nServidor cerrado.')
