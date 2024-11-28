import mysql.connector
from mysql.connector import errorcode
import json
import os

LOGIN_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "db_login.json")
def crear_archivo_login() -> None:
    """
    Crea un archivo JSON en el escritorio llamado "db_login.json" con las cuenta de inicio de sesión.

    Retorna:
        No retorna ningun valor
    """
    if not os.path.exists(LOGIN_FILE):
        cuenta = {
            "usuario": "admin_hospital",
            "contraseña": "test1234*"
        }
        with open(LOGIN_FILE, "w") as file:
            json.dump(cuenta, file, indent=4)
        print(f"Archivo {LOGIN_FILE} creado con éxito en el escritorio.")
    else:
        print(f"El archivo {LOGIN_FILE} ya existe.")
        
def login() ->bool:
    """_
    Inicia sesión en la base de datos.

    Retorna:
        Conexión a la base de datos o False en caso de error.
    """
    try:
        with open(LOGIN_FILE, "r") as file:
            cuenta = json.load(file)
        while True:
            usuario_login = input("Usuario: ")
            contraseña_login = input("Contraseña: ")
            
            if (usuario_login == cuenta["usuario"] and contraseña_login == cuenta["contraseña"]):
                print("Inicio de sesión exitoso.")
                return True
            else:
                print("Error al escribir el usuario o contraseña. Inténtalo de nuevo.")
                
    except FileNotFoundError:
        print(f"No se encontró el archivo {LOGIN_FILE}. Por favor, crea el archivo primero.")
        return False
        
def conectar() -> mysql.connector.MYSQLConnection | None:
    """
    Conecta a la base de datos y selecciona la base de datos "general_hospital".
    
    Retorna:
        Conexión a la base de datos o None en caso de error.
    """
    
    usuario= "admin"
    contraseña="bio4100"
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
            print(err)
            return None

def crear_carpeta_queries() -> None:
    """
    Crea una carpeta llamada "Queries" en caso de que no exista para guardar 
    los archivos json que se generen al hacer una query de busqueda.
    
    Retorna:
     No retorna ningún valor, solo crea la carpeta.
    """
    if not os.path.exists("Queries"):
        os.mkdir("Queries")
        
def obtener_informacion(conexion: mysql.connector.MYSQLConnection, tabla: str, contador: int) -> str:
    """
    Obtiene todos los registros de una tabla y los guarda en un archivo json.
    
    Retorna:
        El nombre del archivo json donde se guardaron los resultados o None si se presenta un error
    
    """
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

def crear_tablas(conexion: mysql.connector.MYSQLConnection) -> bool:
    """
    Crea las tablas que se necesitan en la base de datos.
    
    Returna:
    True si las tablas se crearon correctamente, False en caso contrario.
    """
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
        "  FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE"
        ")"
    )
    tablas['citas'] = (
        "CREATE TABLE IF NOT EXISTS citas ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  medico_id INT,"
        "  paciente_id INT,"
        "  fecha DATE,"
        "  hora TIME,"
        "  FOREIGN KEY (medico_id) REFERENCES medicos(id) ON DELETE CASCADE,"
        "  FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE"
        ")"
    )

    for nombre_tabla in tablas:
        descripcion_tabla = tablas[nombre_tabla]
        try:
            cursor.execute(descripcion_tabla)
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_TABLE_EXISTS_ERROR:
                print(err.msg)
    cursor.close()

def seleccionar_tabla() -> str:
    """
    Selecciona una tabla de la base de datos.
    
    Retorna:
        Nombre de la tabla seleccionada.
    """
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

def verificar_id(conexion: mysql.connector.MYSQLConnection, tabla: str) -> int:
    """
    Verifica que un id exista en una tabla.

    Returna:
        El id si existe, o None si no existe.
    """
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

def añadir_informacion(conexion: mysql.connector.MYSQLConnection, tabla: str) -> bool:
    """
    Añade información a una tabla.
    Retorna:
        True si la información se añadió correctamente, False en caso contrario.
    """
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

def editar_informacion(conexion: mysql.connector.MySQLConnection, tabla:str) -> None:
    """
    Edita información en una tabla.
    Retorna:
        No devuelve ningún  valor, solo actualiza el registro elegido.
    """
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

def eliminar_informacion(conexion: mysql.connector.MySQLConnection, tabla: str) -> None:
    """
    Elimina un registro de una tabla.
    Retorna:
        No devuelve ningún  valor, solo elimina el registro elegido.
    """
    cursor = conexion.cursor()
    try:
        id_registro = verificar_id(conexion,tabla)
        cursor.execute(f"DELETE FROM {tabla} WHERE id = %s", (id_registro,))
        conexion.commit()
        print(f"Registro eliminado de la tabla '{tabla}'.")
    except mysql.connector.Error as err:
        print(f"Error al eliminar información de la tabla '{tabla}': {err}")
    finally:
        cursor.close()

def importar_datos_json(conexion:mysql.connector.MySQLConnection, ruta_archivo:str, tabla:str) -> None: 
    """
    Importa datos desde un archivo json a una tabla de la base de datos.
    Retorna:
        None si no hay errores, sino muestra el error.
    """
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

def menu()-> None:
    """
    Muestra el menú principal y permite seleccionar la opción deseada.
    """
    try:
        crear_carpeta_queries()
        crear_archivo_login()
        if not login():
            print("No se pudo iniciar sesión. Fin del programa")
            return
        conexion = conectar()
        if not conexion:
            print("No se pudo conectar a la base de datos")
            return
        
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
                try:
                    obtener_informacion(conexion, tabla, contador)
                    contador+=1
                except Exception as e:
                    print(f"Error al obtener: {e}")
            elif opcion == 2:
                tabla = seleccionar_tabla()
                try:
                    añadir_informacion(conexion, tabla)
                except Exception as e:
                    print(f"Error al añadir: {e}")
            elif opcion == 3:
                tabla = seleccionar_tabla()
                try:
                    editar_informacion(conexion, tabla)
                except Exception as e:
                    print(f"Error al editar: {e}")
            elif opcion == 4:
                tabla = seleccionar_tabla()
                try:
                    eliminar_informacion(conexion, tabla)
                except Exception as e:
                    print(f"Error al eliminar: {e}")
            elif opcion == 5:
                break
            else:
                print("Ingrese una opcion valida")
    except Exception as error_desconocido:
        print(f"Ocurrió un error imprevisto: {error_desconocido}")
    finally:
        conexion.close()
        print("Conexión cerrada exitosamente")
        

menu()