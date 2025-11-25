import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/entrepreneur.sqlite')

query = '''
SELECT 
    Investor, 
    SUM(Money_Requested) AS Total_Money_Requested
FROM 
    entrepreneur
GROUP BY 
    Investor
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_trail().encode(
    x='Investor:N',
    y='Total_Money_Requested:Q',
    size='Total_Money_Requested:Q'
)

chart.show()