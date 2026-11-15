# Interfaz visual local del laboratorio. Usa únicamente la biblioteca estándar.

from ast import literal_eval
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from pprint import pformat
import json
import threading
import webbrowser

from ejercicio1 import ordenar_diccionarios
from ejercicio2 import calcular_potencias
from ejercicio3 import transponer_matriz
from ejercicio4 import eliminar_elementos


EJERCICIOS = [
    {
        "titulo": "Ordenar diccionarios",
        "descripcion": "Organiza una lista de diccionarios a partir de una de sus claves.",
        "etiqueta": "Lista de diccionarios",
        "ayuda": 'Usa diccionarios entre llaves y textos entre comillas. Ejemplo: [{"nombre": "Ana", "edad": 20}].',
        "datos": '[{"make": "Nokia", "model": 216, "color": "Black"},\n {"make": "Apple", "model": 2, "color": "Silver"},\n {"make": "Huawei", "model": 50, "color": "Gold"},\n {"make": "Samsung", "model": 7, "color": "Blue"}]',
        "extra_etiqueta": "Clave para ordenar",
        "extra": "model",
        "extra_ayuda": "Debe existir en todos los diccionarios. Ejemplo: model, make o color.",
    },
    {
        "titulo": "Calcular potencias",
        "descripcion": "Eleva cada entero de la lista a la potencia n que indiques.",
        "etiqueta": "Lista de números enteros",
        "ayuda": "Escribe los enteros entre corchetes y separados por comas. Ejemplo: [-2, 0, 5].",
        "datos": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        "extra_etiqueta": "Exponente n",
        "extra": "3",
        "extra_ayuda": "Debe ser un número entero positivo, mayor que 0. Ejemplo: 3.",
    },
    {
        "titulo": "Transponer una matriz",
        "descripcion": "Convierte las columnas de tu matriz en las filas de su transpuesta.",
        "etiqueta": "Matriz como lista de listas",
        "ayuda": "Cada fila va entre corchetes y debe tener la misma longitud. Ejemplo: [[1, 2], [3, 4]].",
        "datos": "[[1, 2, 3, 1],\n [4, 5, 6, 0],\n [7, 8, 9, -1]]",
        "extra_etiqueta": "",
        "extra": "",
        "extra_ayuda": "",
    },
    {
        "titulo": "Eliminar elementos",
        "descripcion": "Quita los valores indicados y conserva el orden de los elementos restantes.",
        "etiqueta": "Lista inicial",
        "ayuda": "Puedes usar textos o números. Los textos deben ir entre comillas.",
        "datos": "['rojo', 'verde', 'azul', 'amarillo', 'gris', 'blanco', 'negro']",
        "extra_etiqueta": "Lista de elementos a borrar",
        "extra": "['amarillo', 'café', 'blanco']",
        "extra_ayuda": "Escribe otra lista. Se eliminan todas las apariciones de sus valores.",
    },
]


class ErrorEntrada(ValueError):
    def __init__(self, mensaje, campo="datos"):
        super().__init__(mensaje)
        self.campo = campo


def interpretar_lista(texto, campo="datos"):
    try:
        datos = literal_eval(texto)
    except (ValueError, SyntaxError, TypeError, RecursionError):
        raise ErrorEntrada("Escribe una lista válida, por ejemplo [1, 2] o ['rojo', 'azul'].", campo)
    if not isinstance(datos, list):
        raise ErrorEntrada("Los datos deben ser una lista entre corchetes [].", campo)
    return datos


def calcular(solicitud):
    if not isinstance(solicitud, dict):
        raise ValueError("La solicitud debe contener los datos del ejercicio.")
    ejercicio = solicitud.get("ejercicio")
    if type(ejercicio) is not int or ejercicio not in (1, 2, 3, 4):
        raise ValueError("Selecciona un ejercicio del 1 al 4.")
    texto = solicitud.get("datos")
    extra = solicitud.get("extra", "")
    if not isinstance(texto, str) or not isinstance(extra, str):
        raise ValueError("Completa los campos de datos.")
    datos = interpretar_lista(texto)

    if ejercicio == 1:
        clave = extra.strip()
        if not clave:
            raise ErrorEntrada("Indica la clave para ordenar.", "extra")
        for diccionario in datos:
            if not isinstance(diccionario, dict):
                raise ErrorEntrada("Cada elemento debe ser un diccionario.")
            if clave not in diccionario:
                raise ErrorEntrada(f"La clave '{clave}' debe existir en todos los diccionarios.", "extra")
        try:
            resultado = ordenar_diccionarios(datos, clave)
        except TypeError:
            raise ErrorEntrada("Los valores de la clave deben ser comparables: usa números o textos del mismo tipo.")
    elif ejercicio == 2:
        for numero in datos:
            if type(numero) is not int:
                raise ErrorEntrada("Todos los elementos de la lista deben ser enteros.")
        try:
            n = int(extra)
        except ValueError:
            raise ErrorEntrada("El exponente n debe ser un número entero positivo, mayor que 0.", "extra")
        if n <= 0:
            raise ErrorEntrada("El exponente n debe ser un número entero positivo, mayor que 0.", "extra")
        resultado = calcular_potencias(datos, n)
    elif ejercicio == 3:
        for fila in datos:
            if not isinstance(fila, list):
                raise ErrorEntrada("Cada fila de la matriz debe ser una lista.")
            for valor in fila:
                if type(valor) not in (int, float):
                    raise ErrorEntrada("Los elementos de la matriz deben ser números.")
        try:
            resultado = transponer_matriz(datos)
        except ValueError as error:
            raise ErrorEntrada(str(error))
    else:
        elementos = interpretar_lista(extra, "extra")
        resultado = eliminar_elementos(datos, elementos)

    return {"resultado": pformat(resultado, width=60, sort_dicts=False), "cantidad": len(resultado)}


class InterfazHandler(BaseHTTPRequestHandler):
    def responder(self, estado, contenido, tipo="application/json; charset=utf-8"):
        if isinstance(contenido, (dict, list)):
            contenido = json.dumps(contenido, ensure_ascii=False)
        if isinstance(contenido, str):
            contenido = contenido.encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(contenido)

    def host_valido(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def do_GET(self):
        if not self.host_valido():
            self.responder(403, {"error": "Dirección local no válida."})
            return
        if self.path == "/api/ejercicios":
            self.responder(200, EJERCICIOS)
            return
        archivos = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/estilos.css": ("estilos.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }
        if self.path not in archivos:
            self.responder(404, {"error": "Archivo no encontrado."})
            return
        nombre, tipo = archivos[self.path]
        ruta = Path(__file__).resolve().parent / "interfaz" / nombre
        self.responder(200, ruta.read_bytes(), tipo)

    def do_POST(self):
        origen = f"http://127.0.0.1:{self.server.server_port}"
        if not self.host_valido() or self.headers.get("Origin") != origen:
            self.responder(403, {"error": "Abre la interfaz desde su dirección local."})
            return
        if self.path != "/api/calcular":
            self.responder(404, {"error": "Acción no encontrada."})
            return
        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            if longitud <= 0 or longitud > 65536:
                raise ValueError("Ingresa una lista más pequeña (máximo 64 KB por solicitud).")
            solicitud = json.loads(self.rfile.read(longitud))
            self.responder(200, calcular(solicitud))
        except (ValueError, UnicodeError, RecursionError, OverflowError) as error:
            self.responder(400, {"error": str(error), "campo": getattr(error, "campo", None)})

    def log_message(self, formato, *argumentos):
        pass


def main():
    with ThreadingHTTPServer(("127.0.0.1", 0), InterfazHandler) as servidor:
        direccion = f"http://127.0.0.1:{servidor.server_port}"
        print(f"Interfaz visual: {direccion}", flush=True)
        print("Para cerrar el servidor, cierra esta ventana o presiona Ctrl+C.", flush=True)
        threading.Timer(0.5, webbrowser.open, args=(direccion,)).start()
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nInterfaz cerrada.")


if __name__ == "__main__":
    main()
