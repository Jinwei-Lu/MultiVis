import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/wrestler.sqlite')
query = '''
SELECT Location, Event, SUM(CAST(Days_held AS INT)) AS Total_Days_Held
FROM wrestler
GROUP BY Location, Event
ORDER BY Location, Event
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Location:N',
    y='Total_Days_Held:Q',
    color='Event:N'
)

chart