import mysql.connector
from mysql.connector import errorcode
import json
import os

def conectar():
    while True:
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
            return conexion
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Credenciales incorrectas. Por favor, inténtalo de nuevo.")
            else:
                print(err)
                
def crear_carpeta_queries():
    if not os.path.exists("Queries"):
        os.mkdir("Queries")
        
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

def crear_tablas(conexion):
    cursor = conexion.cursor()
    tablas = {}
    tablas['medicos'] = (
        "CREATE TABLE IF NOT EXISTS medicos ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  nombre VARCHAR(100),"
        "  especialidad VARCHAR(100)"
        ")"
    )
    tablas['pacientes'] = (
        "CREATE TABLE IF NOT EXISTS pacientes ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  nombre VARCHAR(100),"
        "  fecha_nacimiento DATE"
        ")"
    )
    tablas['historia_medica'] = (
        "CREATE TABLE IF NOT EXISTS historia_medica ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  paciente_id INT,"
        "  descripcion TEXT,"
        "  FOREIGN KEY (paciente_id) REFERENCES pacientes(id)"
        ")"
    )
    tablas['citas'] = (
        "CREATE TABLE IF NOT EXISTS citas ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  medico_id INT,"
        "  paciente_id INT,"
        "  fecha DATE,"
        "  hora TIME,"
        "  FOREIGN KEY (medico_id) REFERENCES medicos(id),"
        "  FOREIGN KEY (paciente_id) REFERENCES pacientes(id)"
        ")"
    )

    for nombre_tabla in tablas:
        descripcion_tabla = tablas[nombre_tabla]
        try:
            cursor.execute(descripcion_tabla)
            print(f"Tabla '{nombre_tabla}' creada.")
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_TABLE_EXISTS_ERROR:
                print(err.msg)
    cursor.close()

def seleccionar_tabla():
    tablas = ["medicos", "pacientes", "historia_medica", "citas"]
    while True:
        print("Tablas disponibles:")
        for i, tabla in enumerate(tablas, 1):
            print(f"{i}. {tabla}")
        
        opcion = input("Elige una opción (nombre o número): ")
        try:
            opcion_int = int(opcion)
            if 1 <= opcion_int <= len(tablas):
                return tablas[opcion_int - 1]
            else:
                print("Ingrese una opción válida.")
        except ValueError:
            if opcion in tablas:
                return opcion
            else:
                print("Tabla no válida.")

def obtener_informacion(conexion, tabla):
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM {tabla}")
    resultados = cursor.fetchall()
    for fila in resultados:
        print(fila)
    cursor.close()

def verificar_id(conexion, tabla):
    cursor = conexion.cursor()
    while True:
        try:
            id_elemento = int(input(f"ID del registro en la tabla {tabla}: "))
            cursor.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id_elemento,))
            resultado = cursor.fetchone()
            if resultado:
                return id_elemento
            else:
                print("Ingrese un ID valido")
        except ValueError:
            print("Ingrese un valor numerico")
    cursor.close()

def añadir_informacion(conexion, tabla):
    cursor = conexion.cursor()
    if tabla == "medicos":
        nombre = input("Nombre: ")
        while not nombre.isalpha():
            print("solo letras")
            nombre = input("Nombre: ")
        especialidad = input("Especialidad: ")
        while not especialidad.isalpha():
            print("solo letras")
            especialidad = input("Especialidad: ")
        consulta = "INSERT INTO medicos (nombre, especialidad) VALUES (%s, %s)"
        valores = (nombre, especialidad)
    elif tabla == "pacientes":
        nombre = input("Nombre: ")
        while not nombre.isalpha():
            print("solo letras")
            nombre = input("Nombre: ")
        while True:
          fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ")
          if len(fecha_nacimiento) != 10 or fecha_nacimiento[4] != "-" or fecha_nacimiento[7] != "-":
            print("signo incorrecto")
            continue
          try:
            año = int(fecha_nacimiento[:4])
            mes = int(fecha_nacimiento[5:7])
            dia = int(fecha_nacimiento[8:10])
          except ValueError:
            print("ingrese numeros")
            continue
          if mes < 1 or mes > 12:
            print("Mes incorrecto")
            continue
          if dia < 1 or dia > 31:
            print("Día incorrecto.")
            continue
          break
        consulta = "INSERT INTO pacientes (nombre, fecha_nacimiento) VALUES (%s, %s)"
        valores = (nombre, fecha_nacimiento)
    elif tabla == "historia_medica":
        paciente_id = verificar_id(conexion, "pacientes")
        descripcion = input("Descripción: ")
        consulta = "INSERT INTO historia_medica (paciente_id, descripcion) VALUES (%s, %s)"
        valores = (paciente_id, descripcion)
    elif tabla == "citas":
        medico_id = verificar_id(conexion, "medicos")
        paciente_id = verificar_id(conexion, "pacientes")
        while True:
            fecha = input("Fecha (YYYY-MM-DD): ")
            if len(fecha) != 10 or fecha[4] != "-" or fecha[7] != "-":
                print("signo incorrecto")
                continue
            try:
                año = int(fecha[:4])
                mes = int(fecha[5:7])
                dia = int(fecha[8:10])
            except ValueError:
                print("ingrese numeros")
                continue
            if mes < 1 or mes > 12:
                print("Mes incorrecto")
                continue
            if dia < 1 or dia > 31:
                print("Día incorrecto")
                continue
            break
        while True:
            hora = input("Hora (HH:MM:SS): ")
            if len(hora) != 8 or hora[2] != ":" or hora[5] != ":":
                print("signo incorrecto")
                continue
            try:
                horas = int(hora[:2])
                minutos = int(hora[3:5])
                segundos = int(hora[6:8])
            except ValueError:
                print("ingrese numeros")
                continue
            if horas < 0 or horas > 24:
                print("Hora incorrecta")
                continue
            if minutos < 0 or minutos > 59:
                print("Minutos incorrectos")
                continue
            if segundos < 0 or segundos > 59:
                print("Segundos incorrectos")
                continue
            break

        consulta = "INSERT INTO citas (medico_id, paciente_id, fecha, hora) VALUES (%s, %s, %s, %s)"
        valores = (medico_id, paciente_id, fecha, hora)

    try:
        cursor.execute(consulta, valores)
        conexion.commit()
        print("Información añadida correctamente.")
    except mysql.connector.Error as err:
        print(err)
    cursor.close()

def editar_informacion(conexion, tabla):
    cursor = conexion.cursor()
    id_elemento = verificar_id(conexion, tabla)
    if tabla == "medicos":
        nombre = input("Nuevo nombre: ")
        while not nombre.isalpha():
            print("solo letras")
            nombre = input("Nombre: ")
        especialidad = input("Nueva especialidad: ")
        while not especialidad.isalpha():
            print("solo letras")
            especialidad = input("Especialidad: ")
        consulta = "UPDATE medicos SET nombre = %s, especialidad = %s WHERE id = %s"
        valores = (nombre, especialidad, id_elemento)
    elif tabla == "pacientes":
        nombre = input("Nuevo nombre: ")
        while not nombre.isalpha():
            print("solo letras")
            nombre = input("Nombre: ")
        while True:
          fecha_nacimiento = input("Nueva fecha de nacimiento (YYYY-MM-DD): ")
          if len(fecha_nacimiento) != 10 or fecha_nacimiento[4] != "-" or fecha_nacimiento[7] != "-":
            print("signo incorrecto")
            continue
          try:
            año = int(fecha_nacimiento[:4])
            mes = int(fecha_nacimiento[5:7])
            dia = int(fecha_nacimiento[8:10])
          except ValueError:
            print("ingrese numeros")
            continue
          if mes < 1 or mes > 12:
            print("Mes incorrecto")
            continue
          if dia < 1 or dia > 31:
            print("Día incorrecto.")
            continue
          break
        consulta = "UPDATE pacientes SET nombre = %s, fecha_nacimiento = %s WHERE id = %s"
        valores = (nombre, fecha_nacimiento, id_elemento)
    elif tabla == "historia_medica":
        paciente_id = verificar_id(conexion, "pacientes")
        descripcion = input("Nueva descripción: ")
        consulta = "UPDATE historia_medica SET paciente_id = %s, descripcion = %s WHERE id = %s"
        valores = (paciente_id, descripcion, id_elemento)
    elif tabla == "citas":
        medico_id = verificar_id(conexion, "medicos")
        paciente_id = verificar_id(conexion, "pacientes")
        while True:
          fecha = input("Nueva fecha (YYYY-MM-DD): ")
          if len(fecha) != 10 or fecha[4] != "-" or fecha[7] != "-":
            print("signo incorrecto")
            continue
          try:
            año = int(fecha[:4])
            mes = int(fecha[5:7])
            dia = int(fecha[8:10])
          except ValueError:
            print("ingrese numeros")
            continue
          if mes < 1 or mes > 12:
            print("Mes incorrecto")
            continue
          if dia < 1 or dia > 31:
            print("Día incorrecto")
            continue
          break
        while True:
          hora = input("Nueva hora (HH:MM:SS): ")
          if len(hora) != 8 or hora[2] != ":" or hora[5] != ":":
            print("signo incorrecto")
            continue
          try:
            horas = int(hora[:2])
            minutos = int(hora[3:5])
            segundos = int(hora[6:8])
          except ValueError:
            print("ingrese numeros")
            continue
          if horas < 0 or horas > 24:
            print("Hora incorrecta")
            continue
          if minutos < 0 or minutos > 59:
            print("Minutos incorrectos")
            continue
          if segundos < 0 or segundos > 59:
            print("Segundos incorrectos")
            continue
          break
        consulta = "UPDATE citas SET medico_id = %s, paciente_id = %s, fecha = %s, hora = %s WHERE id = %s"
        valores = (medico_id, paciente_id, fecha, hora, id_elemento)

    try:
        cursor.execute(consulta, valores)
        conexion.commit()
        print("Información editada correctamente.")
    except mysql.connector.Error as err:
        print(err)
    cursor.close()

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

def importar_datos_json(conexion, ruta_archivo, tabla): 
    try: 
        with open(ruta_archivo, 'r') as file: 
            datos = json.load(file) 
        cursor = conexion.cursor() 
        for registro in datos: 
            columnas = ', '.join(registro.keys())
            placeholders = ', '.join(['%s'] * len(registro)) 
            valores = tuple(registro.values()) 
            consulta = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})" 
            cursor.execute(consulta, valores) 
        conexion.commit() 
        print(f"Datos importados correctamente en la tabla {tabla}.") 
    except (mysql.connector.Error, json.JSONDecodeError, FileNotFoundError) as e: 
        print(f"Error al importar datos: {e}") 
    finally: cursor.close()

def menu():
    conexion = conectar()
    crear_carpeta_queries(conexion)
    if conexion:
        crear_tablas(conexion)
        contador=1
        while True:
            try:
                opcion = int(input("Elige una opción:\n1. Obtener Información\n2. Añadir Información\n3. Editar Información\n4. Eliminar Información\n5. Salir\n"))
            except ValueError:
                print("Ingrese un valor numérico")
                continue
            if opcion == 1:
                tabla = seleccionar_tabla()
                obtener_informacion(conexion, tabla, contador)
                contador+=1
            elif opcion == 2:
                tabla = seleccionar_tabla()
                añadir_informacion(conexion, tabla)
            elif opcion == 3:
                tabla = seleccionar_tabla()
                editar_informacion(conexion, tabla)
            elif opcion == 4:
                tabla = seleccionar_tabla()
                eliminar_informacion(conexion, tabla)
            elif opcion == 5:
                break
            else:
                print("Ingrese una opcion valida")
        conexion.close()

menu()