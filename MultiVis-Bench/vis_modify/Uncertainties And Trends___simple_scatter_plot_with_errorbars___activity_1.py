import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/activity_1.sqlite')

query = '''
SELECT
    A.activity_name,
    AVG(S.Age) AS average_age,
    MIN(S.Age) AS min_age,
    MAX(S.Age) AS max_age
FROM
    Participates_in AS P
JOIN
    Student AS S ON P.stuid = S.StuID
JOIN
    Activity AS A ON P.actid = A.actid
GROUP BY
    A.activity_name;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).transform_calculate(
    ymin="datum.min_age",
    ymax="datum.max_age"
)

points = base.mark_point(
    filled=True,
    size=50,
    color='black'
).encode(
    alt.X('activity_name', sort=None),
    alt.Y('average_age', title='Average Age of Participants')
)

errorbars = base.mark_errorbar().encode(
    x="activity_name",
    y="ymin:Q",
    y2="ymax:Q"
)

chart = points + errorbars

chart