import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/customers_and_invoices.sqlite')
query = '''
SELECT 
    date_order_placed AS order_date
FROM 
    Orders
ORDER BY 
    date_order_placed ASC
'''
df = pd.read_sql_query(query, conn)
conn.close()

cumulative_chart = alt.Chart(df).transform_window(
    cumulative_count="count()",
    sort=[{"field": "order_date"}],
).mark_area().encode(
    x=alt.X("order_date:T", title="Order Date"),
    y=alt.Y("cumulative_count:Q", title="Cumulative Count of Orders").stack(False)
)

cumulative_chart