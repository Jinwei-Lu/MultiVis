import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/party_host.sqlite')

query = '''
SELECT 
    p.Party_Theme,
    SUM(p.Number_of_hosts) AS Total_Hosts,
    AVG(CAST(p.Last_year AS INT) - CAST(p.First_year AS INT)) AS Avg_Active_Years
FROM 
    party AS p
GROUP BY 
    p.Party_Theme
ORDER BY 
    Total_Hosts DESC;
'''

df = pd.read_sql_query(query, conn)

conn.close()

base = alt.Chart(df).encode(x=alt.X('Party_Theme:N', title='Party Theme'))

bar = base.mark_bar().encode(
    y=alt.Y('Total_Hosts:Q', title='Total Number of Hosts')
)

line = base.mark_line(color='red').encode(
    y=alt.Y('Avg_Active_Years:Q', title='Average Active Years')
)

chart = (bar + line).resolve_scale(y='independent').properties(width=600)

chart