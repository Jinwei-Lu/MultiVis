import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/museum_visit.sqlite')

query = '''
SELECT 
    m.Name AS Museum_Name,
    v.Num_of_Ticket,
    v.Total_spent
FROM 
    visit AS v
JOIN 
    museum AS m ON v.Museum_ID = m.Museum_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_calculate(
    url='https://www.google.com/search?q=' + alt.datum.Museum_Name
).mark_point().encode(
    x='Num_of_Ticket:Q',
    y='Total_spent:Q',
    href='url:N',
    tooltip=['Museum_Name:N', 'Num_of_Ticket:Q', 'Total_spent:Q']
)

chart.show()