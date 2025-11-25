import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/culture_company.sqlite')

query = '''
SELECT Year, COUNT(*) AS Book_Count
FROM book_club
GROUP BY Year
ORDER BY Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

cumulative_chart = alt.Chart(df).transform_window(
    cumulative_count="sum(Book_Count)",
    sort=[{"field": "Year"}],
).mark_area().encode(
    x=alt.X("Year:Q", title="Year"),
    y=alt.Y("cumulative_count:Q", title="Cumulative Count of Books").stack(False)
)

cumulative_chart