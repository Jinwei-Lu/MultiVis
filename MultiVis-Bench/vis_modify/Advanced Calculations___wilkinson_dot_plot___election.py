import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/election.sqlite')
query = '''
SELECT p.Party, COUNT(e.Delegate) AS Delegate_Count
FROM election AS e
JOIN party AS p ON e.Party = p.Party_ID
GROUP BY p.Party
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_circle(opacity=1).transform_window(
    id='rank()',
    groupby=['Party']
).encode(
    alt.X('Party:N', title='Political Party'),
    alt.Y('id:O').axis(None).sort('descending')
)

chart