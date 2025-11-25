import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/news_report.sqlite')

query = '''
SELECT
    CAST(SUBSTR(T1.Date, LENGTH(T1.Date) - 3) AS INTEGER) AS EventYear,
    COUNT(T1.Event_ID) AS NumberOfEvents,
    AVG(T3.Years_working) AS AverageJournalistExperience
FROM
    event AS T1
JOIN
    news_report AS T2 ON T1.Event_ID = T2.Event_ID
JOIN
    journalist AS T3 ON T2.journalist_ID = T3.journalist_ID
GROUP BY
    EventYear
ORDER BY
    EventYear;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    x=alt.X('EventYear:O', title='Event Year')
)

bars = base.mark_bar().encode(
    y=alt.Y('NumberOfEvents:Q', title='Number of Events')
)

line = base.mark_line(color='red').encode(
    y=alt.Y('AverageJournalistExperience:Q', title='Average Journalist Experience')
)

chart = (bars + line).resolve_scale(
    y='independent'
).properties(
    title='Events per Year and Average Journalist Experience'
)

chart