import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/wrestler.sqlite')

query = '''
SELECT 
    w.Days_held AS Days_Held,
    CAST(substr(e.Time, 4, 2) AS INTEGER) * 60 + CAST(substr(e.Time, 7, 2) AS INTEGER) AS Elimination_Time_Seconds,
    e.Team AS Team
FROM 
    wrestler AS w
JOIN 
    Elimination AS e
ON 
    w.Wrestler_ID = e.Wrestler_ID
WHERE 
    w.Event = 'Live event'
'''

df = pd.read_sql_query(query, conn)

conn.close()

base = alt.Chart(df).mark_circle(opacity=0.5).encode(
    alt.X('Days_Held:Q', title='Days Held'),
    alt.Y('Elimination_Time_Seconds:Q', title='Elimination Time (Seconds)'),
    alt.Color('Team:N', title='Team')
)

chart = base + base.transform_loess('Days_Held', 'Elimination_Time_Seconds', groupby=['Team']).mark_line(size=4)

chart.properties(
    title="Relationship Between Days Held and Elimination Time by Team"
)