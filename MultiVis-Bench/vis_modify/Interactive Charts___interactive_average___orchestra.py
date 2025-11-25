import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/orchestra.sqlite')

query = '''
SELECT Date, Type, `Official_ratings_(millions)` AS Official_ratings
FROM performance;
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval(encodings=['x'])

bars = alt.Chart(df).mark_bar().encode(
    x='Date:O',
    y='Official_ratings:Q',
    color='Type:N',
    opacity=alt.condition(brush, alt.value(1), alt.value(0.7))
).add_params(
    brush
)

line = alt.Chart(df).mark_rule(color='firebrick').encode(
    y='mean(Official_ratings):Q',
    size=alt.SizeValue(3)
).transform_filter(
    brush
)

chart = alt.layer(bars, line).properties(
    title='Official Ratings of Performance Types Over Time with Average Line (Interactive)'
)

chart.show()