import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/customer_deliveries.sqlite')

query = '''
SELECT
    date(date_became_customer) AS year,
    COUNT(customer_id) AS num_customers
FROM Customers
GROUP BY
    year
ORDER BY
    year;
'''

df = pd.read_sql_query(query, conn)

df['cumulative_customers'] = df['num_customers'].cumsum()

conn.close()

alt.Chart(df).mark_line().encode(
    x='year:O',
    y=alt.Y('cumulative_customers', scale=alt.Scale(type="log"), title='Cumulative Number of Customers')
).properties(
    title='Customer Growth Over Time (Logarithmic Scale)'
)