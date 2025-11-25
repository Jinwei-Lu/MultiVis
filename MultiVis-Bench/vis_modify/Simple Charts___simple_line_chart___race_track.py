import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/race_track.sqlite')

query = '''
SELECT 
    t.Name AS Track_Name,
    COUNT(r.Race_ID) AS Race_Count
FROM 
    track AS t
LEFT JOIN 
    race AS r ON t.Track_ID = r.Track_ID
GROUP BY 
    t.Track_ID
ORDER BY 
    t.Track_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line().encode(
    x='Track_Name:N',
    y='Race_Count:Q'
)

chart