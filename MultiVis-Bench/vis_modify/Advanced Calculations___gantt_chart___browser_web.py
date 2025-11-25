import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/browser_web.sqlite')
query = '''
SELECT id, name
FROM Web_client_accelerator
'''
df = pd.read_sql_query(query, conn)
conn.close()
df['start'] = df['id']
df['end'] = df['id'] + 2
df = df.rename(columns={'name': 'task'})
chart = alt.Chart(df).mark_bar().encode(
    x='start:Q',
    x2='end:Q',
    y='task:N'
)
chart