import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/epinions_1.sqlite')

query = '''
SELECT 
    ua.name AS user_name,
    r.rank AS rank,
    SUM(r.rating) AS total_rating
FROM 
    review AS r
JOIN 
    useracct AS ua ON r.u_id = ua.u_id
GROUP BY 
    ua.name, r.rank
ORDER BY 
    ua.name, r.rank
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_area().encode(
    x=alt.X("rank:Q", title="Rank"),
    y=alt.Y("total_rating:Q", title="Total Rating"),
    color=alt.Color("user_name:N", title="User"),
    row=alt.Row("user_name:N", title="User", sort=alt.EncodingSortField(field="total_rating", op="sum", order="descending"))
).properties(
    height=50,
    width=400
)

chart.show()