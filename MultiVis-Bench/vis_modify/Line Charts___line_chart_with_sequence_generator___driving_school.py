import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/driving_school.sqlite')

query = '''
SELECT 
    DATE(datetime_payment) AS payment_date,
    payment_method_code,
    SUM(amount_payment) AS total_payment
FROM 
    Customer_Payments
GROUP BY 
    payment_date, payment_method_code
ORDER BY 
    payment_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

line_chart = alt.Chart(df).mark_line().encode(
    x=alt.X('payment_date:T', title='Payment Date'),
    y=alt.Y('sum(total_payment):Q', title='Cumulative Payment Amount'),
    color=alt.Color('payment_method_code:N', title='Payment Method')
).transform_window(
    cumulative_sum='sum(total_payment)',
    frame=[None, 0],
    groupby=['payment_method_code']
).encode(
    y=alt.Y('cumulative_sum:Q', title='Cumulative Payment Amount')
)

line_chart