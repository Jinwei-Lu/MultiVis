import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/candidate_poll.sqlite')

query = '''
SELECT Poll_Source, Candidate_ID
FROM candidate
ORDER BY Candidate_ID
'''

df = pd.read_sql_query(query, conn)

conn.close()

df['start'] = df['Candidate_ID']
df['end'] = df['Candidate_ID'] + 1
df['task'] = df['Poll_Source']

chart = alt.Chart(df).mark_bar().encode(
    x='start',
    x2='end',
    y='task'
)

chart