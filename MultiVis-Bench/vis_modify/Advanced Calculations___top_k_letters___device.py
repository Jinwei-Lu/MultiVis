import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/device.sqlite')

query = '''
SELECT Software_Platform, COUNT(*) AS Platform_Count
FROM device
GROUP BY Software_Platform
ORDER BY Platform_Count DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

alt.Chart(df).transform_window(
    rank='rank(Platform_Count)',
    sort=[alt.SortField('Platform_Count', order='descending')]
).transform_filter(
    alt.datum.rank < 6
).mark_bar().encode(
    y=alt.Y('Software_Platform:N').sort('-x'),
    x='Platform_Count:Q'
)