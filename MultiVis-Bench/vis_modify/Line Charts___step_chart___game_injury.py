import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/game_injury.sqlite')
query = '''
SELECT 
    g.Season AS season,
    COUNT(i.id) AS injury_count
FROM 
    game AS g
JOIN 
    injury_accident AS i ON g.id = i.game_id
GROUP BY 
    g.Season
ORDER BY 
    g.Season
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line(interpolate='step-after').encode(
    x=alt.X('season:O', title='Season'),
    y=alt.Y('injury_count:Q', title='Total Injuries')
).properties(
    title='Total Injuries Per Season'
)

chart