import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/climbing.sqlite')

query = '''
SELECT Mountain_ID, Height
FROM mountain
ORDER BY Mountain_ID;
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df, width=600).mark_line().transform_window(
    sort=[{'field': 'Mountain_ID'}],
    frame=[None, 0],
    cumulative_height='sum(Height)'
).encode(
    x='Mountain_ID:O',
    y='cumulative_height:Q'
)

chart