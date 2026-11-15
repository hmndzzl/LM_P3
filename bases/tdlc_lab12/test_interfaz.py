# Pruebas del controlador visual, sin instalar dependencias.

import ast
import unittest
from interfaz import EJERCICIOS, ErrorEntrada, calcular


class PruebasInterfaz(unittest.TestCase):
    def calcular(self, ejercicio, datos, extra=""):
        respuesta = calcular({"ejercicio": ejercicio, "datos": datos, "extra": extra})
        return ast.literal_eval(respuesta["resultado"])

    def test_ejemplos_del_enunciado(self):
        esperados = [
            [2, 7, 50, 216],
            [1, 8, 27, 64, 125, 216, 343, 512, 729, 1000],
            [[1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 0, -1]],
            ['rojo', 'verde', 'azul', 'gris', 'negro'],
        ]
        for numero, ejemplo in enumerate(EJERCICIOS, 1):
            with self.subTest(ejercicio=numero):
                resultado = self.calcular(numero, ejemplo['datos'], ejemplo['extra'])
                if numero == 1:
                    resultado = [diccionario['model'] for diccionario in resultado]
                self.assertEqual(resultado, esperados[numero - 1])

    def test_datos_propios(self):
        self.assertEqual(self.calcular(1, "[{'edad': 20}, {'edad': 18}]", 'edad'), [{'edad': 18}, {'edad': 20}])
        self.assertEqual(self.calcular(2, '[-2, 0, 5]', '2'), [4, 0, 25])
        self.assertEqual(self.calcular(3, '[[1, 2, 3], [4, 5, 6]]'), [[1, 4], [2, 5], [3, 6]])
        self.assertEqual(self.calcular(4, '[1, 2, 1, 3, 3]', '[1, 99]'), [2, 3, 3])

    def test_listas_vacias(self):
        for numero, extra in [(1, 'clave'), (2, '3'), (3, ''), (4, '[]')]:
            with self.subTest(ejercicio=numero):
                self.assertEqual(self.calcular(numero, '[]', extra), [])

    def test_datos_invalidos(self):
        casos = [
            (1, '[1]', 'model'),
            (1, "[{'a': 1}]", 'b'),
            (1, "[{'a': 1}, {'a': 'x'}]", 'a'),
            (2, '[1.5]', '3'),
            (2, '[True]', '3'),
            (2, '[1]', '0'),
            (2, '[1]', '-2'),
            (2, '[1]', '2.5'),
            (2, '[1]', ''),
            (3, '[1, 2]', ''),
            (3, '[[1], [2, 3]]', ''),
            (3, "[['texto']]", ''),
            (4, '(1, 2)', '[]'),
            (4, '[1]', 'texto'),
            (4, '__import__("sys").exit()', '[]'),
        ]
        for numero, datos, extra in casos:
            with self.subTest(ejercicio=numero, datos=datos, extra=extra):
                with self.assertRaises(ValueError):
                    self.calcular(numero, datos, extra)

    def test_solicitudes_invalidas(self):
        for solicitud in [None, [], {}, {'ejercicio': True}, {'ejercicio': 5}, {'ejercicio': 2, 'datos': []}]:
            with self.subTest(solicitud=solicitud):
                with self.assertRaises(ValueError):
                    calcular(solicitud)

    def test_errores_identifican_el_campo_a_corregir(self):
        casos = [
            (1, "[{'nombre': 'Ana'}]", "edad", "extra"),
            (2, "[1, 2]", "0", "extra"),
            (2, "[1, 2]", "2.5", "extra"),
            (2, "[1.5]", "3", "datos"),
            (3, "[[1], [2, 3]]", "", "datos"),
            (4, "[1]", "texto", "extra"),
        ]
        for numero, datos, extra, campo in casos:
            with self.subTest(ejercicio=numero, campo=campo):
                with self.assertRaises(ErrorEntrada) as error:
                    self.calcular(numero, datos, extra)
                self.assertEqual(error.exception.campo, campo)


if __name__ == '__main__':
    unittest.main()
