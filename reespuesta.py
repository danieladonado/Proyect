import mysql.connector
import json
import os
from mysql.connector import errorcode

# Función para conectar a la base de datos
def conectar():
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")
    base_datos = "general_hospital"
    try:
        conexion = mysql.connector.connect(
            host="127.0.0.1",
            user=usuario,
            password=contraseña
        )
        cursor = conexion.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {base_datos}")
        conexion.database = base_datos
        print(f"Conectado a la base de datos '{base_datos}'.")
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
        return None

# Crear la carpeta "Queries" si no existe
def crear_carpeta_queries():
    if not os.path.exists("Queries"):
        os.mkdir("Queries")

# Función para obtener información de una tabla y guardarla como JSON
def obtener_informacion(conexion, tabla, contador):
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM {tabla}")
        resultados = cursor.fetchall()
        if resultados:
            archivo_json = f"Queries/{tabla}_{contador}.json"
            with open(archivo_json, "w") as archivo:
                json.dump(resultados, archivo, indent=4, default=str)
            print(f"Resultados guardados en {archivo_json}")
        else:
            print(f"No se encontraron registros en la tabla '{tabla}'.")
    except mysql.connector.Error as err:
        print(f"Error al obtener información de la tabla '{tabla}': {err}")
    finally:
        cursor.close()

# Función para añadir información a una tabla
def añadir_informacion(conexion, tabla):
    cursor = conexion.cursor()
    try:
        if tabla == "medicos":
            nombre = input("Nombre del médico: ")
            especialidad = input("Especialidad: ")
            cursor.execute("INSERT INTO medicos (nombre, especialidad) VALUES (%s, %s)", (nombre, especialidad))
        elif tabla == "pacientes":
            nombre = input("Nombre del paciente: ")
            fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ")
            cursor.execute("INSERT INTO pacientes (nombre, fecha_nacimiento) VALUES (%s, %s)", (nombre, fecha_nacimiento))
        elif tabla == "historia_medica":
            paciente_id = int(input("ID del paciente: "))
            descripcion = input("Descripción de la historia médica: ")
            cursor.execute("INSERT INTO historia_medica (paciente_id, descripcion) VALUES (%s, %s)", (paciente_id, descripcion))
        elif tabla == "citas":
            medico_id = int(input("ID del médico: "))
            paciente_id = int(input("ID del paciente: "))
            fecha = input("Fecha (YYYY-MM-DD): ")
            hora = input("Hora (HH:MM:SS): ")
            cursor.execute("INSERT INTO citas (medico_id, paciente_id, fecha, hora) VALUES (%s, %s, %s, %s)", (medico_id, paciente_id, fecha, hora))
        conexion.commit()
        print(f"Información añadida a la tabla '{tabla}' correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al añadir información a la tabla '{tabla}': {err}")
    finally:
        cursor.close()

# Función para editar información en una tabla
def editar_informacion(conexion, tabla):
    cursor = conexion.cursor()
    try:
        id_registro = int(input(f"ID del registro a editar en '{tabla}': "))
        if tabla == "medicos":
            nuevo_nombre = input("Nuevo nombre: ")
            nueva_especialidad = input("Nueva especialidad: ")
            cursor.execute("UPDATE medicos SET nombre = %s, especialidad = %s WHERE id = %s", (nuevo_nombre, nueva_especialidad, id_registro))
        elif tabla == "pacientes":
            nuevo_nombre = input("Nuevo nombre: ")
            nueva_fecha = input("Nueva fecha de nacimiento (YYYY-MM-DD): ")
            cursor.execute("UPDATE pacientes SET nombre = %s, fecha_nacimiento = %s WHERE id = %s", (nuevo_nombre, nueva_fecha, id_registro))
        conexion.commit()
        print(f"Registro actualizado en la tabla '{tabla}'.")
    except mysql.connector.Error as err:
        print(f"Error al editar la tabla '{tabla}': {err}")
    finally:
        cursor.close()

# Función para eliminar información de una tabla
def eliminar_informacion(conexion, tabla):
    cursor = conexion.cursor()
    try:
        id_registro = int(input(f"ID del registro a eliminar en '{tabla}': "))
        cursor.execute(f"DELETE FROM {tabla} WHERE id = %s", (id_registro,))
        conexion.commit()
        print(f"Registro eliminado de la tabla '{tabla}'.")
    except mysql.connector.Error as err:
        print(f"Error al eliminar información de la tabla '{tabla}': {err}")
    finally:
        cursor.close()

# Seleccionar tabla
def seleccionar_tabla():
    tablas = ["medicos", "pacientes", "historia_medica", "citas"]
    print("Tablas disponibles:", ", ".join(tablas))
    tabla = input("Selecciona una tabla: ")
    if tabla in tablas:
        return tabla
    else:
        print("Tabla no válida.")
        return None

# Menú principal
def menu():
    conexion = conectar()
    if conexion:
        crear_carpeta_queries()
        contador = 1
        while True:
            try:
                opcion = int(input("\nElige una opción:\n1. Obtener Información\n2. Añadir Información\n3. Editar Información\n4. Eliminar Información\n5. Salir\n"))
            except ValueError:
                print("Por favor, ingresa un número.")
                continue
            if opcion == 1:
                tabla = seleccionar_tabla()
                if tabla:
                    obtener_informacion(conexion, tabla, contador)
                    contador += 1
            elif opcion == 2:
                tabla = seleccionar_tabla()
                if tabla:
                    añadir_informacion(conexion, tabla)
            elif opcion == 3:
                tabla = seleccionar_tabla()
                if tabla:
                    editar_informacion(conexion, tabla)
            elif opcion == 4:
                tabla = seleccionar_tabla()
                if tabla:
                    eliminar_informacion(conexion, tabla)
            elif opcion == 5:
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida.")
        conexion.close()

# Ejecutar el programa
menu()
