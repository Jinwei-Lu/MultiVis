import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/products_for_hire.sqlite')

query = '''
SELECT 
    strftime('%Y', booking_start_date) AS year,
    strftime('%m', booking_start_date) AS month,
    SUM(amount_payable) AS total_amount_payable
FROM Bookings
GROUP BY year, month
ORDER BY year, month
'''

df = pd.read_sql_query(query, conn)
conn.close()

heatmap = alt.Chart(df).mark_rect().encode(
    x=alt.X('month:O', title='Month'),
    y=alt.Y('year:O', title='Year'),
    color=alt.Color('total_amount_payable:Q', title='Total Amount Payable')
).properties(
    title='Total Amount Payable by Month and Year'
)

heatmap