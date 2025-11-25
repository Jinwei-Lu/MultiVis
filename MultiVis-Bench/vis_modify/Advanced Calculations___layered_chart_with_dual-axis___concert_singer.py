import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/concert_singer.sqlite')

query = '''
SELECT Name, Capacity, Average
FROM stadium;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    alt.X('Name:N').title('Stadium Name')
)

bars = base.mark_bar(color='#57A44C').encode(
    alt.Y('Capacity:Q').axis(title='Stadium Capacity', titleColor='#57A44C')
)

line = base.mark_line(color='#5276A7').encode(
    alt.Y('Average:Q').axis(title='Average Attendance', titleColor='#5276A7')
)

chart = alt.layer(bars, line).resolve_scale(
    y='independent'
)

chart