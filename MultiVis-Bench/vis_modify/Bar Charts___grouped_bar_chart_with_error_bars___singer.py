import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/singer.sqlite')
query = '''
SELECT Citizenship, AVG(Net_Worth_Millions) AS Avg_Net_Worth, 
       COUNT(*) AS Singer_Count, 
       MIN(Net_Worth_Millions) AS Min_Net_Worth, 
       MAX(Net_Worth_Millions) AS Max_Net_Worth
FROM singer
GROUP BY Citizenship
'''
df = pd.read_sql_query(query, conn)
conn.close()

bars = alt.Chart(df).mark_bar().encode(
    x='Citizenship:N',
    y=alt.Y('Avg_Net_Worth:Q').title('Average Net Worth (Millions)'),
    color='Citizenship:N'
)

error_bars = alt.Chart(df).mark_errorbar(extent='ci').encode(
    x='Citizenship:N',
    y=alt.Y('Min_Net_Worth:Q').title('Net Worth Range'),
    y2='Max_Net_Worth:Q'
)

chart = alt.layer(bars, error_bars).properties(
    title='Comparison of Average Net Worth by Citizenship with Variability'
)

chart.show()