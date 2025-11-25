import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/performance_attendance.sqlite')
query = '''
SELECT Location, Attendance
FROM performance
'''
df = pd.read_sql_query(query, conn)
conn.close()

points = alt.Chart(df).mark_point().encode(
    x='Attendance:Q',
    y='Location:N'
)

text = points.mark_text(
    align='left',
    baseline='middle',
    dx=7
).encode(
    text='Location:N'
)

points + text