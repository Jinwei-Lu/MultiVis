import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/driving_school.sqlite')
query = '''
SELECT V.vehicle_details AS vehicle_type, L.price
FROM Lessons AS L
JOIN Vehicles AS V ON L.vehicle_id = V.vehicle_id
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df, height=100).mark_circle(opacity=1).transform_window(
    id='rank()',
    groupby=['vehicle_type', 'price']
).encode(
    alt.X('price:Q', title='Lesson Price'),
    alt.Y('id:O').axis(None).sort('descending'),
    alt.Color('vehicle_type:N', title='Vehicle Type')
).properties(
    title='Distribution of Lesson Prices by Vehicle Type'
)

chart