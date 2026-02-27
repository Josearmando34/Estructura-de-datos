import time

def fibonacci_recursivo(n):
    if n <= 1:
        return n
    else:
        return fibonacci_recursivo(n-1) + fibonacci_recursivo(n-2)
    
n = int(input("Ingresa un número para calcular Fibonacci (recursivo): "))

inicio = time.time()
resultado = fibonacci_recursivo(n)
fin = time.time()

print("Resultado:", resultado)
print("Tiempo de ejecución:", fin - inicio, "segundos")