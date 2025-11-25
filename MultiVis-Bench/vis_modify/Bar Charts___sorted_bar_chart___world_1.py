import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/world_1.sqlite')

query = '''
SELECT Name, Population
FROM city
ORDER BY Population DESC
LIMIT 10
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Population:Q',
    y=alt.Y('Name:N').sort('-x')
)

chart.show()