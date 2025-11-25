import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/decoration_competition.sqlite')

query = '''
SELECT 
    c.Name AS College_Name,
    AVG(r.Rank_in_Round) AS Avg_Rank
FROM 
    round AS r
JOIN 
    member AS m ON r.Member_ID = m.Member_ID
JOIN 
    college AS c ON m.College_ID = c.College_ID
GROUP BY 
    c.College_ID
ORDER BY 
    Avg_Rank DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    alt.X('College_Name:N').sort('-y'),
    alt.Y('Avg_Rank:Q'),
    alt.Color('Avg_Rank:Q')
).transform_window(
    rank='rank(Avg_Rank)',
    sort=[alt.SortField('Avg_Rank', order='descending')]
).transform_filter(
    (alt.datum.rank < 6)
)

chart.show()