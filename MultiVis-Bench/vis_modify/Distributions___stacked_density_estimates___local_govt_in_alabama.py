import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/local_govt_in_alabama.sqlite')
query = '''
SELECT Service_ID, Service_Type_Code
FROM Services
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_fold(
    fold=['Service_ID'],
    as_=['Measurement_type', 'value']
).transform_density(
    density='value',
    bandwidth=0.3,
    groupby=['Service_Type_Code'],
    extent=[0, 10],
    counts=True,
    steps=200
).mark_area().encode(
    alt.X('value:Q'),
    alt.Y('density:Q').stack('zero'),
    alt.Color('Service_Type_Code:N')
).properties(width=400, height=100)

chart.show()