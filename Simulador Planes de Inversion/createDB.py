import pymysql

def crear_db():
    try:
        connection = pymysql.Connection(host='database-1.co4sycnzigyw.us-east-1.rds.amazonaws.com', user="admin", password="qwerty12345", db="mysql")
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS moneidapp")

        connection.close()
        cursor.close()

        connection = pymysql.Connection(host="database-1.co4sycnzigyw.us-east-1.rds.amazonaws.com", user="admin", password="qwerty12345", db="moneidapp")
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



