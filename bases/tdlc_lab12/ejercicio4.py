# Ejercicio 4: eliminar elementos indicados de una lista usando lambda.


def eliminar_elementos(lista, elementos_a_borrar):
    # Devuelve los elementos restantes en su orden original.
    conservar = lambda elemento: elemento not in elementos_a_borrar
    restantes = []

    for elemento in lista:
        if conservar(elemento):
            restantes.append(elemento)

    return restantes
