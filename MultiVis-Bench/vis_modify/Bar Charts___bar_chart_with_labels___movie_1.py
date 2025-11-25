import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/movie_1.sqlite')

query = '''
SELECT 
    M.title AS MovieTitle,
    AVG(R.stars) AS AverageRating
FROM 
    Rating AS R
JOIN 
    Movie AS M ON R.mID = M.mID
GROUP BY 
    M.mID, M.title
ORDER BY 
    AverageRating DESC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    x=alt.X('AverageRating:Q', title='Average Rating'),
    y=alt.Y('MovieTitle:N', sort='-x', title='Movie Title'),
    text=alt.Text('AverageRating:Q', format='.2f')
)

chart = base.mark_bar() + base.mark_text(align='left', dx=2)
chart.properties(title="Average Movie Ratings")