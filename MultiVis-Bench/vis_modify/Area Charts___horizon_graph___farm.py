import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/farm.sqlite')

query = '''
SELECT Year, Total_Cattle
FROM farm
ORDER BY Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

area1 = alt.Chart(df).mark_area(
    clip=True,
    interpolate='monotone',
    opacity=0.6
).encode(
    alt.X('Year:O').scale(zero=False, nice=False),
    alt.Y('Total_Cattle:Q').scale(domain=[0, 5000]).title('Total Cattle (0-5000)'),
).properties(
    width=500,
    height=75
)

area2 = area1.encode(
    alt.Y('ny:Q').scale(domain=[0, 5000])
).transform_calculate(
    "ny", alt.datum.Total_Cattle - 5000
)

area1 + area2