import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/music_4.sqlite')

query = '''
SELECT 
    a.Artist, COUNT(v.Song) AS Song_Count
FROM 
    artist AS a
JOIN 
    volume AS v ON a.Artist_ID = v.Artist_ID
GROUP BY 
    a.Artist
'''

df = pd.read_sql_query(query, conn)
conn.close()

bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('Artist:N', title='Artist'),
    y=alt.Y('Song_Count:Q', title='Number of Songs on Top')
)

rule = alt.Chart(df).mark_rule(color='red').encode(
    y='mean(Song_Count):Q'
)

(bar + rule).properties(width=600)