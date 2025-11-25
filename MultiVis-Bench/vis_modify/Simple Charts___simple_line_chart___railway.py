import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/railway.sqlite')

query = '''
SELECT 
    r.Built AS Year,
    COUNT(t.Train_ID) AS Train_Count
FROM 
    railway AS r
LEFT JOIN 
    train AS t ON r.Railway_ID = t.Railway_ID
WHERE 
    r.Built != '' AND r.Built != 'Unknown'
GROUP BY 
    r.Built
ORDER BY 
    CAST(r.Built AS INTEGER)
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line().encode(
    x=alt.X('Year:N', title='Year Built'),
    y=alt.Y('Train_Count:Q', title='Number of Trains')
).properties(
    title="Number of Trains Managed by Railways Over Time"
)

chart