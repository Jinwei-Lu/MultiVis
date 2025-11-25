import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/journal_committee.sqlite')

query = '''
SELECT 
    e.Age AS Editor_Age,
    j.Sales AS Journal_Sales,
    COUNT(jc.Work_Type) AS Contribution_Count
FROM 
    editor AS e
JOIN 
    journal_committee AS jc ON e.Editor_ID = jc.Editor_ID
JOIN 
    journal AS j ON jc.Journal_ID = j.Journal_ID
GROUP BY 
    e.Editor_ID, j.Journal_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_point().encode(
    x='Editor_Age:Q',
    y='Journal_Sales:Q',
    size='Contribution_Count:Q'
)

chart.show()