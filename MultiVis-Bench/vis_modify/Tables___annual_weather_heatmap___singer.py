import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/singer.sqlite')

query = '''
SELECT 
    s.Birth_Year AS Singer_Birth_Year,
    so.Title AS Song_Title,
    MIN(so.Highest_Position) AS Best_Position
FROM 
    singer AS s
JOIN 
    song AS so
ON 
    s.Singer_ID = so.Singer_ID
GROUP BY 
    s.Birth_Year, so.Title
ORDER BY 
    s.Birth_Year ASC, Best_Position ASC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df, title="Best Chart Positions by Singer Birth Year").mark_rect().encode(
    alt.X("Song_Title:N").title("Song Title"),
    alt.Y("Singer_Birth_Year:N").title("Singer Birth Year"),
    alt.Color("Best_Position:Q").title("Highest Position"),
    tooltip=[
        alt.Tooltip("Song_Title", title="Song Title"),
        alt.Tooltip("Singer_Birth_Year", title="Singer Birth Year"),
        alt.Tooltip("Best_Position", title="Best Position"),
    ],
).configure_view(
    step=13,
    strokeWidth=0
).configure_axis(
    domain=False
)

chart.show()