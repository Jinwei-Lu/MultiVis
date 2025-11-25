import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/school_bus.sqlite')
query = '''
SELECT sb.Years_Working, COUNT(*) AS Driver_Count
FROM school_bus AS sb
JOIN driver AS d ON sb.Driver_ID = d.Driver_ID
GROUP BY sb.Years_Working
ORDER BY sb.Years_Working
'''
df = pd.read_sql_query(query, conn)
conn.close()

initial_range = (5, 10)
brush = alt.selection_interval(encodings=['x'], value={'x': initial_range})

base = alt.Chart(df, width=600, height=200).mark_bar().encode(
    x=alt.X('Years_Working:Q', title='Years Working'),
    y=alt.Y('Driver_Count:Q', title='Number of Drivers')
)

upper = base.encode(
    alt.X('Years_Working:Q').scale(domain=brush)
)

lower = base.properties(
    height=60
).add_params(brush)

chart = upper & lower
chart