import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/club_1.sqlite')

query = '''
SELECT Sex, COUNT(*) AS count
FROM Student
GROUP BY Sex;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    alt.Theta("count:Q").stack(True),
    alt.Color("Sex:N").legend(None)
)

pie = base.mark_arc(outerRadius=120)
text = base.mark_text(radius=140, size=20).encode(text="Sex:N")

chart = pie + text
chart