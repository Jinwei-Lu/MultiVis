import sqlite3
import pandas as pd
import altair as alt
import datetime as dt

conn = sqlite3.connect('database/school_player.sqlite')

query = '''
SELECT School, Year_Entered_Competition, Enrollment
FROM school
WHERE Year_Entered_Competition IS NOT NULL AND Enrollment IS NOT NULL
ORDER BY Year_Entered_Competition
'''

df = pd.read_sql_query(query, conn)

conn.close()

date_range = (dt.date(1900, 1, 1), dt.date(2000, 1, 1))

brush = alt.selection_interval(encodings=['x'], value={'x': date_range})

base = alt.Chart(df, width=600, height=200).mark_line(point=True).encode(
    x=alt.X('Year_Entered_Competition:T', title='Year Entered Competition'),
    y=alt.Y('Enrollment:Q', title='Enrollment'),
    tooltip=['School:N', 'Year_Entered_Competition:T', 'Enrollment:Q']
)

upper = base.encode(
    alt.X('Year_Entered_Competition:T').scale(domain=brush)
)

lower = base.properties(
    height=60
).add_params(brush)

chart = upper & lower

chart