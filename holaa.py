meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

categorias = ["Ropa", "Deportes", "Juguetería"]

ventas = [
    [120, 80, 150],
    [110, 90, 140],
    [130, 95, 160],
    [125, 100, 155],
    [140, 110, 170],
    [150, 120, 180],
    [160, 130, 190],
    [155, 125, 185],
    [145, 115, 175],
    [150, 120, 180],
    [170, 140, 210],
    [200, 160, 300]
]

def mostrar_tabla():
    print("\n" + "=" * 55)
    print("{:<3} {:<12} {:>10} {:>12} {:>14}".format(
        "#", "Mes", "Ropa", "Deportes", "Juguetería"
    ))
    print("-" * 55)

    for i in range(len(meses)):
        print("{:<3} {:<12} {:>10.2f} {:>12.2f} {:>14.2f}".format(
            i + 1,
            meses[i],
            ventas[i][0],
            ventas[i][1],
            ventas[i][2]
        ))
    print("=" * 55)

def modificar_monto():
    mostrar_tabla()
    mes = int(input("\nSelecciona el mes (1-12): ")) - 1

    print("\nDepartamentos:")
    for i, cat in enumerate(categorias):
        print(f"{i+1}. {cat}")

    categoria = int(input("Selecciona el departamento (1-3): ")) - 1
    nuevo_monto = float(input("Ingresa el nuevo monto: "))

    ventas[mes][categoria] = nuevo_monto
    print("✅ Monto modificado correctamente")

def eliminar_elemento():
    mostrar_tabla()
    mes = int(input("\nSelecciona el mes (1-12): ")) - 1

    print("\nDepartamentos:")
    for i, cat in enumerate(categorias):
        print(f"{i+1}. {cat}")

    categoria = int(input("Selecciona el departamento (1-3): ")) - 1
    ventas[mes][categoria] = 0
    print("🗑️ Elemento eliminado")

def buscar_mes_departamento():
    print("\nBuscar por mes:")
    for i, mes in enumerate(meses):1
    print(f"{i+1}. {mes}")

    mes = int(input("Selecciona el mes (1-12): ")) - 1

    print("\nBuscar por departamento:")
    for i, cat in enumerate(categorias):
        print(f"{i+1}. {cat}")

    categoria = int(input("Selecciona el departamento (1-3): ")) - 1

    monto = ventas[mes][categoria]

    print("\n🔍 Resultado de la búsqueda")
    print("-" * 35)
    print(f"Mes: {meses[mes]}")
    print(f"Departamento: {categorias[categoria]}")

    if monto == 0:
        print("Monto: ELIMINADO (0)")
    else:
        print(f"Monto: {monto:.2f}")

while True:
    print("\n===== MENÚ PRINCIPAL =====")
    print("1. Mostrar tabla")
    print("2. Modificar un monto")
    print("3. Eliminar un elemento")
    print("4. Buscar por mes y departamento")
    print("5. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        mostrar_tabla()
    elif opcion == "2":
        modificar_monto()
    elif opcion == "3":
        eliminar_elemento()
    elif opcion == "4":
        buscar_mes_departamento()
    elif opcion == "5":
        print("👋 Programa finalizado")
        break
    else:
        print("❌ Opción inválida")

