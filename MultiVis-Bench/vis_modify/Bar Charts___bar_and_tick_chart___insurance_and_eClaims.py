import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_and_eClaims.sqlite')

query = '''
SELECT 
    Claim_Type_Code AS claim_type,
    SUM(Amount_Claimed) AS total_claimed,
    AVG(Amount_Piad) AS avg_paid
FROM 
    Claim_Headers
GROUP BY 
    Claim_Type_Code
'''

df = pd.read_sql_query(query, conn)
conn.close()

bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('claim_type:N', title='Claim Type'),
    y=alt.Y('total_claimed:Q', title='Total Amount Claimed')
).properties(width=alt.Step(40))

tick = alt.Chart(df).mark_tick(
    color='red',
    thickness=2,
    size=40 * 0.9,
).encode(
    x=alt.X('claim_type:N', title='Claim Type'),
    y=alt.Y('avg_paid:Q', title='Average Amount Paid')
)

chart = bar + tick
chart