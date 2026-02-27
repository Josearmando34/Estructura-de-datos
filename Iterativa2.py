import time

def fibonacci_iterativo(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b

# Programa interactivo
n = int(input("Ingresa un número para calcular Fibonacci (iterativo): "))

inicio = time.time()
resultado = fibonacci_iterativo(n)
fin = time.time()

print("Resultado:", resultado)
print("Tiempo de ejecución:", fin - inicio, "segundos")