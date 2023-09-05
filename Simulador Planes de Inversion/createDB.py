import pymysql

def crear_db():
    try:
        connection = pymysql.Connection(host='localhost', user="root", password="Daz00575#", db="mysql")
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS moneidapp")

        connection.close()
        cursor.close()

        connection = pymysql.Connection(host="localhost", user="root", password="Daz00575#", db="moneidapp")
        cursor = connection.cursor()

        cursor.execute("SHOW DATABASES")
        connection.commit()
        connection.close()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
        print("Éxito")

crear_db()        



