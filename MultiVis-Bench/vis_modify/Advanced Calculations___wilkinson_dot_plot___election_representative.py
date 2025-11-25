import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/election_representative.sqlite')

query = '''
SELECT r.Party, SUM(e.Seats) AS Total_Seats
FROM election AS e
JOIN representative AS r ON e.Representative_ID = r.Representative_ID
GROUP BY r.Party
ORDER BY Total_Seats DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

dot_data = []
for _, row in df.iterrows():
    dot_data.extend([row['Party']] * int(row['Total_Seats']))

dot_df = pd.DataFrame({'Party': dot_data})

chart = alt.Chart(dot_df, height=100).mark_circle(opacity=1).transform_window(
    id='rank()',
    groupby=['Party']
).encode(
    alt.X('Party:N', title='Political Party'),
    alt.Y('id:O').axis(None).sort('descending')
)

chart