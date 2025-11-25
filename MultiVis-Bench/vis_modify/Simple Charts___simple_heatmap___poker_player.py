import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/poker_player.sqlite')
query = '''
SELECT 
    p.Nationality,
    pp.Final_Table_Made,
    SUM(pp.Earnings) AS Total_Earnings
FROM 
    poker_player AS pp
JOIN 
    people AS p ON pp.People_ID = p.People_ID
GROUP BY 
    p.Nationality, pp.Final_Table_Made
ORDER BY 
    p.Nationality, pp.Final_Table_Made;
'''
df = pd.read_sql_query(query, conn)
conn.close()

heatmap = alt.Chart(df).mark_rect().encode(
    x=alt.X('Final_Table_Made:O', title='Final Tables Made'),
    y=alt.Y('Nationality:O', title='Nationality'),
    color=alt.Color('Total_Earnings:Q', title='Total Earnings', scale=alt.Scale(scheme='viridis'))
).properties(
    width=600,
    height=400,
    title="Heatmap of Poker Players' Earnings by Nationality and Final Tables Made"
)

heatmap