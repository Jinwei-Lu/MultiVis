import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/game_1.sqlite')

query = '''
SELECT VG.GType AS Game_Type, SUM(PG.Hours_Played) AS Total_Hours_Played
FROM Plays_Games AS PG
JOIN Video_Games AS VG ON PG.GameID = VG.GameID
GROUP BY VG.GType
ORDER BY Total_Hours_Played DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line(interpolate='step-after').encode(
    x=alt.X('Game_Type:N', title='Game Type'),
    y=alt.Y('Total_Hours_Played:Q', title='Total Hours Played')
).properties(
    title='Total Hours Played by Game Type'
)

chart