import mysql.connector
from getpass import getpass

username = input("MySQL 用户名：")
password = getpass("MySQL 密码：")

def get_order(connection, order_id):
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT order_id, order_status, amount FROM orders WHERE order_id = %s",
            (order_id,),)
        return cursor.fetchone()

with mysql.connector.connect(
    host = "127.0.0.1",
    port = 3306,
    user = username,
    password = password,
    database = "qa_training",
) as connection:
    print(get_order(connection, 1002))
    print(get_order(connection, 9999))
