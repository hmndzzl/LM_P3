# Ejercicio 2: calcular potencias de una lista de enteros usando lambda.


def calcular_potencias(lista, n):
    # Devuelve una lista con cada entero elevado al exponente positivo n.
    if type(n) is not int or n <= 0:
        raise ValueError("El exponente debe ser un entero positivo.")

    potencia = lambda numero: numero ** n
    resultado = []

    for numero in lista:
        valor = potencia(numero)
        resultado.append(valor)

    return resultado
