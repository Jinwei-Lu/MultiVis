import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/railway.sqlite')

query = '''
SELECT 
    T1.Location AS Location,
    COUNT(T2.Train_ID) AS Train_Count
FROM 
    railway AS T1
JOIN 
    train AS T2 ON T1.Railway_ID = T2.Railway_ID
GROUP BY 
    T1.Location
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_joinaggregate(
    TotalTrains='sum(Train_Count)',
).transform_calculate(
    PercentOfTotal="datum.Train_Count / datum.TotalTrains"
).mark_bar().encode(
    alt.X('PercentOfTotal:Q').axis(format='.0%'),
    y='Location:N'
)

chart.show()