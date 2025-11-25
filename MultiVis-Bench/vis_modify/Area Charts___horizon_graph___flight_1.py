import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/flight_1.sqlite')

query = '''
SELECT 
    a.name AS aircraft_name,
    SUM(f.distance) AS total_distance
FROM 
    flight AS f
JOIN 
    aircraft AS a ON f.aid = a.aid
GROUP BY 
    a.name
ORDER BY 
    total_distance DESC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

area1 = alt.Chart(df).mark_area(
    clip=True,
    interpolate='monotone',
    opacity=0.6
).encode(
    alt.X('aircraft_name:N').title('Aircraft Type'),
    alt.Y('total_distance:Q').scale(domain=[0, 5000]).title('Distance (miles)'),
).properties(
    width=500,
    height=75
)

area2 = area1.encode(
    alt.Y('adjusted_distance:Q').scale(domain=[0, 5000])
).transform_calculate(
    "adjusted_distance", alt.datum.total_distance - 5000
)

final_chart = area1 + area2
final_chart