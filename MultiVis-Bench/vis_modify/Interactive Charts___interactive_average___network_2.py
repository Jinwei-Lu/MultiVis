import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/network_2.sqlite')

query = '''
SELECT 
    P.city AS city, 
    AVG(PF.year) AS avg_years
FROM 
    PersonFriend AS PF
JOIN 
    Person AS P ON PF.name = P.name
GROUP BY 
    P.city
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval(encodings=['x'])

bars = alt.Chart(df).mark_bar().encode(
    x=alt.X('city:N', title='City'),
    y=alt.Y('avg_years:Q', title='Average Years of Friendship'),
    opacity=alt.condition(brush, alt.value(1), alt.value(0.7)),
).add_params(
    brush
)

line = alt.Chart(df).mark_rule(color='firebrick').encode(
    y='mean(avg_years):Q',
    size=alt.SizeValue(3)
).transform_filter(
    brush
)

chart = alt.layer(bars, line)
chart.display()