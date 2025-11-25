import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/department_management.sqlite')

query = '''
SELECT h.born_state AS state, COUNT(*) AS head_count
FROM head AS h
GROUP BY h.born_state
ORDER BY head_count DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_window(
    rank='rank(head_count)',
    sort=[alt.SortField('head_count', order='descending')]
).transform_filter(
    alt.datum.rank < 11
).mark_bar().encode(
    y=alt.Y('state:N').sort('-x'),
    x='head_count:Q'
)

chart.show()