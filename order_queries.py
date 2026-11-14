def get_order(connection, order_id):
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT order_id, order_status, amount FROM orders 
            WHERE order_id = %s""",
            (order_id,),)
        return cursor.fetchone()

def insert_order(connection, order_id, customer_id, amount, order_status):
    with connection.cursor() as cursor:
        cursor.execute(
            """ 
            INSERT INTO orders (order_id, customer_id, amount, 
            order_status, created_at) 
            VALUES (%s, %s, %s, %s, current_date() )
            """, # 多行SQL语句，用三引号括起来
            (order_id, customer_id, amount, order_status),
        )
        