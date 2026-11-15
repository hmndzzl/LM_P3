# Ejercicio 1: ordenar una lista de diccionarios usando lambda.


def ordenar_diccionarios(lista, clave):
    # Devuelve una nueva lista ordenada de menor a mayor por la clave indicada.
    obtener_valor = lambda diccionario: diccionario[clave]
    lista_ordenada = sorted(lista, key=obtener_valor)
    return lista_ordenada
