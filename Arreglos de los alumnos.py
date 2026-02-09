import random
import time
import sys

inicio_tiempo = time.time()

TOTAL_ALUMNOS = 100_0000
TOTAL_MATERIAS = 10_000

alumno = int(input("Ingresa el número del alumno (1 a 100000): "))
materia = int(input("Ingresa el número de la materia (1 a 10000): "))

if not (1 <= alumno <= TOTAL_ALUMNOS and 1 <= materia <= TOTAL_MATERIAS):
    print("Alumno o materia fuera de rango")
    sys.exit()

col_inicio = max(0, alumno - 4)
col_fin = min(TOTAL_ALUMNOS, alumno + 3)

fila_inicio = max(0, materia - 4)
fila_fin = min(TOTAL_MATERIAS, materia + 3)

print("\nTABLA DE CALIFICACIONES (Vista Parcial)\n")

print("Materia \\ Alumno", end="  ")
for a in range(col_inicio, col_fin):
    print(f"A{a+1:^7}", end=" ")
print()

print("-" * (20 + (col_fin - col_inicio) * 9))

# Generar valores al vuelo
for m in range(fila_inicio, fila_fin):
    print(f"Materia {m+1:<6} ", end="")
    for a in range(col_inicio, col_fin):
        valor = random.randint(0, 10)
        if m == materia - 1 and a == alumno - 1:
            print(f"[{valor:^5}]", end=" ")
            calificacion_final = valor
        else:
            print(f" {valor:^5} ", end=" ")
    print()

fin_tiempo = time.time()

print("\nRESULTADO BUSCADO")
print("------------------------------")
print(f"Alumno {alumno}")
print(f"Materia {materia}")
print(f"Calificación: {calificacion_final}")

print("\nTIEMPO DE EJECUCIÓN")
print("------------------------------")
print(f"{fin_tiempo - inicio_tiempo:.4f} segundos")