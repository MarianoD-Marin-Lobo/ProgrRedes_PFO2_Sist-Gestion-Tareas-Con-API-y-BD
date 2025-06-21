import requests
from getpass import getpass

BASE_URL = "http://127.0.0.1:5000"

def registrar_usuario():
    print("\n--- Registro de Usuario ---")
    usuario = input("Nombre de usuario: ")
    contrasena = getpass("Contraseña: ")

    payload = {
        "usuario": usuario,
        "contrasena": contrasena
    }

    response = requests.post(f"{BASE_URL}/registro", json=payload)

    if response.status_code == 201:
        print("✅ Registro exitoso.")
    elif response.status_code == 409:
        print("⚠️ El usuario ya existe.")
    else:
        print(f"❌ Error en el registro: {response.json()}")

def iniciar_sesion():
    print("\n--- Inicio de Sesión ---")
    usuario = input("Usuario: ")
    contrasena = getpass("Contraseña: ")

    response = requests.post(f"{BASE_URL}/login", auth=(usuario, contrasena))

    if response.status_code == 200:
        print("✅ Login exitoso.")
        acceder_a_tareas(usuario, contrasena)
    else:
        print("❌ Credenciales inválidas.")

def acceder_a_tareas(usuario, contrasena):
    print("\n--- Accediendo a /tareas ---")
    response = requests.get(f"{BASE_URL}/tareas", auth=(usuario, contrasena))

    if response.status_code == 200:
        print("✅ Acceso exitoso. Mostrando HTML:")
        print(response.text)  # muestra el HTML que devuelve el servidor
    else:
        print("❌ No se pudo acceder a /tareas.")

def menu():
    while True:
        print("\n=== MENÚ ===")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Salir")
        opcion = input("Seleccioná una opción: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            print("👋 Adiós.")
            break
        else:
            print("⚠️ Opción inválida.")

if __name__ == "__main__":
    menu()
