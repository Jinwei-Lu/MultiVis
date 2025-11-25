import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/race_track.sqlite')

query = '''
SELECT 
    t.Location AS Track_Location,
    COUNT(r.Race_ID) AS Race_Count
FROM 
    race AS r
JOIN 
    track AS t
ON 
    r.Track_ID = t.Track_ID
GROUP BY 
    t.Location
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df).transform_joinaggregate(
    TotalRaces='sum(Race_Count)',
).transform_calculate(
    PercentOfTotal="datum.Race_Count / datum.TotalRaces"
).mark_bar().encode(
    alt.X('PercentOfTotal:Q').axis(format='.0%'),
    y='Track_Location:N'
)

chart.show()