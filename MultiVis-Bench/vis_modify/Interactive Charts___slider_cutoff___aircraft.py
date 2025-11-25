import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/aircraft.sqlite')
query = '''
SELECT Airport_Name, Total_Passengers
FROM airport
ORDER BY Total_Passengers DESC
'''
df = pd.read_sql_query(query, conn)
conn.close()

slider = alt.binding_range(min=0, max=int(df['Total_Passengers'].max()), step=100000)
cutoff = alt.param(bind=slider, value=int(df['Total_Passengers'].median()))
predicate = alt.datum.Total_Passengers < cutoff

chart = alt.Chart(df).mark_bar().encode(
    x='Total_Passengers:Q',
    y=alt.Y('Airport_Name:N', sort='-x'),
    color=alt.when(predicate).then(alt.value("blue")).otherwise(alt.value("red")),
).add_params(
    cutoff
)

chart.show()