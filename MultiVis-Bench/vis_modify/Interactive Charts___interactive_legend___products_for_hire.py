import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/products_for_hire.sqlite')

query = '''
SELECT 
    payment_type_code AS Payment_Type,
    SUM(amount_paid) AS Total_Amount_Paid
FROM Payments
GROUP BY payment_type_code
'''

df = pd.read_sql_query(query, conn)
conn.close()

selection = alt.selection_point(fields=['Payment_Type'], bind='legend')

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Payment_Type:N', title='Payment Type'),
    y=alt.Y('Total_Amount_Paid:Q', title='Total Amount Paid'),
    color=alt.Color('Payment_Type:N', scale=alt.Scale(scheme='category20b')),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_params(
    selection
).properties(
    title='Total Amount Paid by Payment Type'
)

chart.show()