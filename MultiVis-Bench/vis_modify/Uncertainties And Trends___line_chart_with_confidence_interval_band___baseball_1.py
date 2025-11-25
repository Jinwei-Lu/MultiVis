import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/baseball_1.sqlite')

query = '''
SELECT 
    year, 
    team_id, 
    SUM(hr) AS team_hr
FROM batting
WHERE hr IS NOT NULL
GROUP BY year, team_id;
'''

df = pd.read_sql_query(query, conn)
conn.close()

line = alt.Chart(df).mark_line().encode(
    x=alt.X('year:O', title='Year'),
    y=alt.Y('mean(team_hr):Q', title='Average Home Runs per Team')
)

band = alt.Chart(df).mark_errorband(extent='ci').encode(
    x='year:O',
    y=alt.Y('team_hr:Q')
)

chart = (band + line).properties(
    title='Average Team Home Runs per Year with 95% Confidence Interval'
)
chart.show()