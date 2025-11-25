import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/game_injury.sqlite')

query = """
SELECT
  Season,
  Competition,
  COUNT(id) AS game_count
FROM game
GROUP BY Season, Competition
ORDER BY Season, Competition
"""

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_area().encode(
    x=alt.X('Season:O', title='Season'),
    y=alt.Y('game_count:Q', stack='normalize', title='Proportion of Games'),
    color='Competition:N'
).properties(
    title='Proportion of Game Competitions Over Seasons'
)

chart