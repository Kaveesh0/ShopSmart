from datetime import datetime
from sql_connection import get_sql_connection

def insert_order(connection, order):
    cursor = connection.cursor()

    # Insert into orders table
    order_query = ("INSERT INTO orders "
                   "(customer_name, total, datetime) "
                   "VALUES (%s, %s, %s)")
    order_data = (order['customer_name'], order['grand_total'], datetime.now())
    cursor.execute(order_query, order_data)
    orders_id = cursor.lastrowid  # Corrected variable name to orders_id

    # Insert into order_details table
    order_details_query = ("INSERT INTO order_details "
                           "(orders_id, product_id, quantity, total_price) "
                           "VALUES (%s, %s, %s, %s)")
    order_details_data = []
    for order_detail_record in order['order_details']:
        order_details_data.append([
            orders_id,
            int(order_detail_record['product_id']),
            float(order_detail_record['quantity']),
            float(order_detail_record['total_price'])
        ])
    cursor.executemany(order_details_query, order_details_data)

    connection.commit()
    cursor.close()

    return orders_id  # Corrected return value to orders_id

def get_order_details(connection, orders_id):
    cursor = connection.cursor()

    # Fetch order details with product information
    query = ("SELECT order_details.orders_id, order_details.quantity, order_details.total_price, "
             "products.name, products.price_per_unit "
             "FROM order_details "
             "LEFT JOIN products ON order_details.product_id = products.product_id "
             "WHERE order_details.orders_id = %s")
    data = (orders_id, )
    cursor.execute(query, data)
    records = []
    for (orders_id, quantity, total_price, product_name, price_per_unit) in cursor.fetchall():
        records.append({
            'orders_id': orders_id,
            'quantity': quantity,
            'total_price': total_price,
            'product_name': product_name,
            'price_per_unit': price_per_unit
        })

    cursor.close()
    return records

def get_all_orders(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM orders"
    cursor.execute(query)
    response = []
    for (orders_id, customer_name, total, dt) in cursor.fetchall():
        response.append({
            'orders_id': orders_id,
            'customer_name': customer_name,
            'total': total,
            'datetime': dt,
        })

    cursor.close()

    # Append order details in each order
    for record in response:
        record['order_details'] = get_order_details(connection, record['orders_id'])

    return response

if __name__ == '__main__':
    connection = get_sql_connection()
    print(get_all_orders(connection))
    # print(get_order_details(connection, 4))
    # print(insert_order(connection, {
    #     'customer_name': 'dhaval',
    #     'grand_total': 500,  # Adjusted to match the order parameter name
    #     'order_details': [
    #         {
    #             'product_id': 1,
    #             'quantity': 2,
    #             'total_price': 50
    #         },
    #         {
    #             'product_id': 3,
    #             'quantity': 1,
    #             'total_price': 30
    #         }
    #     ]
    # }))
