import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/wrestler.sqlite')

query = '''
SELECT 
    w.Days_held, 
    e.Time, 
    e.Team
FROM 
    wrestler AS w
JOIN 
    Elimination AS e
ON 
    w.Wrestler_ID = e.Wrestler_ID
WHERE 
    w.Days_held != '' AND e.Time != ''
'''

df = pd.read_sql_query(query, conn)
conn.close()

df['Days_held'] = pd.to_numeric(df['Days_held'], errors='coerce')
df['Time'] = df['Time'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

chart = alt.Chart(df).mark_circle().encode(
    x=alt.X('Days_held', title='Days Held'),
    y=alt.Y('Time', title='Elimination Time (seconds)'),
    color='Team'
).interactive()

chart.show()