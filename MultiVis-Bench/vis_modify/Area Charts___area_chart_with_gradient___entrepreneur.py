import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/entrepreneur.sqlite')

query = '''
SELECT 
    p.Date_of_Birth AS date,
    e.Investor AS investor,
    SUM(e.Money_Requested) AS total_money_requested
FROM entrepreneur AS e
JOIN people AS p ON e.People_ID = p.People_ID
GROUP BY p.Date_of_Birth, e.Investor
ORDER BY p.Date_of_Birth
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_filter(
    'datum.investor === "Duncan Bannatyne"'
).mark_area(
    line={'color': 'darkblue'},
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='white', offset=0),
               alt.GradientStop(color='darkblue', offset=1)],
        x1=1,
        x2=1,
        y1=1,
        y2=0
    )
).encode(
    alt.X('date:T', title='Date of Birth'),
    alt.Y('total_money_requested:Q', title='Cumulative Money Requested')
)

chart