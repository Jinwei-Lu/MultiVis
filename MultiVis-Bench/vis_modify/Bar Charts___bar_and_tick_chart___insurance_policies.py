import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_policies.sqlite')

query = '''
SELECT 
    CP.Policy_Type_Code AS Policy_Type,
    SUM(C.Amount_Claimed) AS Total_Amount_Claimed,
    SUM(C.Amount_Settled) AS Total_Amount_Settled
FROM 
    Customer_Policies AS CP
JOIN 
    Claims AS C ON CP.Policy_ID = C.Policy_ID
GROUP BY 
    CP.Policy_Type_Code
'''

df = pd.read_sql_query(query, conn)
conn.close()

bar = alt.Chart(df).mark_bar().encode(
    x='Policy_Type',
    y='Total_Amount_Claimed'
).properties(
    width=alt.Step(40)
)

tick = alt.Chart(df).mark_tick(
    color='red',
    thickness=2,
    size=40 * 0.9
).encode(
    x='Policy_Type',
    y='Total_Amount_Settled'
)

chart = bar + tick
chart