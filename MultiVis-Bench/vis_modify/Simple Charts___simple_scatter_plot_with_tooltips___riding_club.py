import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/riding_club.sqlite')

query = '''
SELECT 
    c.Club_name, 
    c.Region, 
    m.Gold, 
    m.Points
FROM 
    club AS c
JOIN 
    match_result AS m
ON 
    c.Club_ID = m.Club_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()

scatter_plot = alt.Chart(df).mark_circle(size=60).encode(
    x='Gold:Q',
    y='Points:Q',
    color='Region:N',
    tooltip=['Club_name:N', 'Region:N', 'Gold:Q', 'Points:Q']
).interactive()

scatter_plot