import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_policies.sqlite')

query = '''
SELECT 
    Claims.Claim_ID,
    Claims.Amount_Claimed,
    Claims.Amount_Settled,
    (Claims.Amount_Claimed - Claims.Amount_Settled) AS Difference,
    Customer_Policies.Policy_Type_Code
FROM 
    Claims
JOIN 
    Customer_Policies ON Claims.Policy_ID = Customer_Policies.Policy_ID
WHERE 
    strftime('%Y', Claims.Date_Claim_Made) = '2017'
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_point().encode(
    x='Amount_Claimed:Q',
    y='Amount_Settled:Q',
    size='Difference:Q',
    color='Policy_Type_Code:N'
).properties(
    title='Relationship Between Amount Claimed and Amount Settled (2017)'
)

chart.show()