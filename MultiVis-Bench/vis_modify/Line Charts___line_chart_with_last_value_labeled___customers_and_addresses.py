import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/customers_and_addresses.sqlite')

query = '''
SELECT 
    DATE(order_date) AS order_date, 
    COUNT(order_id) AS total_orders
FROM 
    Customer_Orders
GROUP BY 
    DATE(order_date)
ORDER BY 
    order_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).encode(
    x=alt.X("order_date:T", title="Order Date"),
    y=alt.Y("total_orders:Q", title="Total Orders")
)

line = chart.mark_line().encode()

label = chart.encode(
    x='max(order_date):T',
    y=alt.Y('total_orders:Q').aggregate(argmax='order_date'),
    text=alt.Text('total_orders:Q', format='.0f')
)

text = label.mark_text(align='left', dx=4)
circle = label.mark_circle()
final_chart = line + circle + text

final_chart