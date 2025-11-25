import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/workshop_paper.sqlite')

query = '''
SELECT College, AVG(Scores) AS Average_Score
FROM submission
GROUP BY College
ORDER BY Average_Score DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Average_Score:Q',
    y=alt.Y('College:N').sort('-x')
)

chart.show()