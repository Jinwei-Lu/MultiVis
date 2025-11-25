import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/activity_1.sqlite')

query = '''
SELECT 
    S.Age, 
    COUNT(P.actid) AS ActivityCount, 
    S.Major
FROM 
    Student AS S
LEFT JOIN 
    Participates_in AS P ON S.StuID = P.stuid
GROUP BY 
    S.StuID, S.Age, S.Major
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_circle().encode(
    x='Age:Q',
    y='ActivityCount:Q',
    color='Major:N'
).interactive()

chart.show()