import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/orchestra.sqlite')
query = """
SELECT
    P.Type,
    AVG(S.Attendance) AS Average_Attendance,
    AVG(P."Official_ratings_(millions)") AS Average_Official_Ratings
FROM Performance AS P
JOIN Show AS S
    ON P.Performance_ID = S.Performance_ID
GROUP BY
    P.Type;
"""
df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    x='Type:N'
).properties(
    width=600
)

bar = base.mark_bar().encode(
    y='Average_Attendance:Q'
)

line = base.mark_line(color='red').encode(
    y='Average_Official_Ratings:Q'
)

(bar + line).resolve_scale(
    y='independent'
)