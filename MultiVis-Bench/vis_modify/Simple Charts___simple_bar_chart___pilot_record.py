import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/pilot_record.sqlite')

query = '''
SELECT 
    SUBSTR(Date, 1, 4) AS Year,
    COUNT(*) AS Total_Flights
FROM pilot_record
GROUP BY Year
ORDER BY Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Year:N',
    y='Total_Flights:Q'
)

chart