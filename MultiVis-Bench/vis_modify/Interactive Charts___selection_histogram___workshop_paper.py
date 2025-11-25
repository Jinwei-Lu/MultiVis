import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/workshop_paper.sqlite')

query = '''
SELECT 
    w.Name AS Workshop_Name,
    a.Result AS Acceptance_Result,
    COUNT(*) AS Count
FROM 
    Acceptance AS a
JOIN 
    workshop AS w ON a.Workshop_ID = w.Workshop_ID
GROUP BY 
    w.Name, a.Result
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval()

points = alt.Chart(df).mark_bar().encode(
    x='Workshop_Name:N',
    y='Count:Q',
    color=alt.condition(brush, 'Acceptance_Result:N', alt.value('lightgray'))
).add_params(
    brush
)

bars = alt.Chart(df).mark_bar().encode(
    y='Acceptance_Result:N',
    color='Acceptance_Result:N',
    x='sum(Count):Q'
).transform_filter(
    brush
)

points & bars