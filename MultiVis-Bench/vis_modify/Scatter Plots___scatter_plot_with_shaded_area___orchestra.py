import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/orchestra.sqlite')

query = '''
SELECT Age, Year_of_Work
FROM conductor
'''

df = pd.read_sql_query(query, conn)
conn.close()

shaded_area = pd.DataFrame({
    "x1": [40],
    "x2": [42]
})

points = alt.Chart(df).mark_point().encode(
    x=alt.X("Age:Q", title="Conductor Age"),
    y=alt.Y("Year_of_Work:Q", title="Years of Work")
)

interval = alt.Chart(shaded_area).mark_rect(opacity=0.3, color="#FF0000").encode(
    x="x1:Q",
    x2="x2:Q"
)

chart = points + interval
chart