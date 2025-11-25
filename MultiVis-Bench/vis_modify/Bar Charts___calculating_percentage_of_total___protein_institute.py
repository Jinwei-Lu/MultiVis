import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/protein_institute.sqlite')

query = '''
SELECT Name, Height_feet
FROM building
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df).transform_joinaggregate(
    TotalHeight='sum(Height_feet)',
).transform_calculate(
    PercentOfTotal="datum.Height_feet / datum.TotalHeight"
).mark_bar().encode(
    alt.X('PercentOfTotal:Q').axis(format='.0%'),
    y='Name:N'
)

chart.show()