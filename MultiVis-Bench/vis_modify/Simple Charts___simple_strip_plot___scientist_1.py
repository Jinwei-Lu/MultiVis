import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/scientist_1.sqlite')

query = '''
SELECT Code, Hours
FROM Projects
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df).mark_tick().encode(
    x='Hours:Q',
    y='Code:O'
)

chart.show()