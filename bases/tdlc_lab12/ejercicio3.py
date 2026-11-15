# Ejercicio 3: calcular la transpuesta de una matriz usando lambda.


def transponer_matriz(matriz):
    # Devuelve la transpuesta como lista de listas, sin modificar la matriz.
    if not matriz:
        return []

    columnas = len(matriz[0])
    for fila in matriz:
        if len(fila) != columnas:
            raise ValueError("Todas las filas deben tener la misma longitud.")

    obtener_elemento = lambda fila, columna: matriz[fila][columna]
    transpuesta = []

    for columna in range(columnas):
        nueva_fila = []
        for fila in range(len(matriz)):
            valor = obtener_elemento(fila, columna)
            nueva_fila.append(valor)
        transpuesta.append(nueva_fila)

    return transpuesta
