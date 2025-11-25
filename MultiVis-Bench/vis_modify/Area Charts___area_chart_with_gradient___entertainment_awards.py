import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/entertainment_awards.sqlite')

query = '''
SELECT Year, SUM(Num_of_Audience) AS Total_Audience
FROM festival_detail
WHERE Location = 'United States'
GROUP BY Year
ORDER BY Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_area(
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
    alt.X('Year:T', title='Year'),
    alt.Y('Total_Audience:Q', title='Total Number of Audiences')
)

chart