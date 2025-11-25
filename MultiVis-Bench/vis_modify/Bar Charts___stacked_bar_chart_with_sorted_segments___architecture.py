import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/architecture.sqlite')

query = '''
SELECT 
    a.nationality AS nationality,
    SUM(b.length_meters) AS total_length_meters
FROM 
    architect AS a
JOIN 
    bridge AS b ON a.id = b.architect_id
GROUP BY 
    a.nationality
ORDER BY 
    a.nationality ASC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='sum(total_length_meters):Q',
    y='nationality:N',
    color='nationality:N',
    order=alt.Order(
        'nationality',
        sort='ascending'
    )
).properties(
    title="Total Length of Bridges by Architect Nationality"
)

chart