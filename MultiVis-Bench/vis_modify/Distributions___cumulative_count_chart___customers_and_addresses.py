import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/customers_and_addresses.sqlite')

query = '''
SELECT 
    order_status, 
    order_date
FROM 
    Customer_Orders
ORDER BY 
    order_date ASC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

df['order_date'] = pd.to_datetime(df['order_date'])

cumulative_chart = alt.Chart(df).transform_window(
    cumulative_count="count()",
    sort=[{"field": "order_date"}],
    groupby=["order_status"]
).mark_area().encode(
    x=alt.X("order_date:T", title="Order Date"),
    y=alt.Y("cumulative_count:Q", stack=False, title="Cumulative Count"),
    color=alt.Color("order_status:N", title="Order Status")
).properties(
    title="Cumulative Count of Orders by Status Over Time"
)

cumulative_chart