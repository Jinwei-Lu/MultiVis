import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/body_builder.sqlite')
query = '''
SELECT p.Birth_Place AS BirthPlace, SUM(b.Total) AS TotalWeightLifted
FROM body_builder AS b
JOIN people AS p ON b.People_ID = p.People_ID
GROUP BY p.Birth_Place
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
    theta="TotalWeightLifted:Q",
    color="BirthPlace:N"
)

chart