import pymysql

def insertar_datos():
    try:
        connection = pymysql.Connection(host="localhost", user="root", password="Daz00575#", db="moneidapp")
        cursor = connection.cursor()
        sql01 = "INSERT INTO `sucursales` (`id`, `nombreSucursal`, `direccion`, `telefono`) VALUES (%s, %s, %s, %s)"
        sql02 = "INSERT INTO `sucursales` (`id`, `nombreSucursal`, `direccion`, `telefono`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql01, (0o1, "Moneid Matriz", "Boulevard del lago 100", "7772255505"))
        cursor.execute(sql02, (0o2, "Moneid Sucursal 1", "Sixto Gorjon no. 127", "3746880423"))
        sql03 = "INSERT INTO `roles` (`id`, `tipoRol`) VALUES (%s, %s)"
        sql04 = "INSERT INTO `roles` (`id`, `tipoRol`) VALUES (%s, %s)"
        cursor.execute(sql03, (0o1, "Administrador"))
        cursor.execute(sql04, (0o2, "Colaborador"))

        connection.commit()
        connection.close()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
        print("EXITO")

def crear_usuario():
    try:
        # Inicializa la conexión utilizando una DB previamente creada.
        connection = pymysql.Connection(host="localhost", user="root", password="Daz00575#", db="moneidapp")
        cursorr = connection.cursor()
        sql = "INSERT INTO `empleados` (`id`, `username`, `apellidoPAtEmpleado`, `apellidoMatEmpleado`, `password`, `correoElectronico`, `estadoEmpleado`, `creado`, `idSucursalesEmpleado`, `idRolEmpleado`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursorr.execute(sql, (0o1, "Administrador", "Moneid", "Sumax", 'sha256$BOl2pwcjY6kKSgCi$25b90dc07cfc3099088d58222a05544ee896904dbff68c962942beab4e23f8c8', "admin@moneidoficial.com", "Activo", "2023-07-31 13:30:41", 0o1, 0o1))
        #user:admin pass:qwerty
        connection.commit()
        connection.close()
        cursorr.close()
    except Exception as e:
        print(e)
    finally:
        print("\nÉxito🔥")


insertar_datos()
crear_usuario()
