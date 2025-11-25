import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_fnol.sqlite')

query = '''
SELECT 
    C.Customer_name AS customer_name,
    COUNT(Cl.Claim_ID) AS total_claims
FROM 
    Customers AS C
JOIN 
    First_Notification_of_Loss AS FNOL ON C.Customer_ID = FNOL.Customer_ID
JOIN 
    Claims AS Cl ON FNOL.FNOL_ID = Cl.FNOL_ID
GROUP BY 
    C.Customer_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()
average_claims = df['total_claims'].mean()
df['average_claims'] = average_claims

bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('customer_name:N', title='Customer Name'),
    y=alt.Y('total_claims:Q', title='Total Claims')
).properties(
    width=alt.Step(40)
)

tick = alt.Chart(df).mark_tick(
    color='red',
    thickness=2,
    size=40 * 0.9
).encode(
    x=alt.X('customer_name:N', title='Customer Name'),
    y=alt.Y('average_claims:Q', title='Average Claims')
)

chart = bar + tick
chart