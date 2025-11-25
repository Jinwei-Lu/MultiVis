import altair as alt
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/cre_Theme_park.sqlite')
query = '''
SELECT CAST(Tourist_ID AS TEXT) AS age, Visit_ID AS people FROM Visits
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_boxplot(extent='min-max').encode(
    x='age:O',
    y='people:Q'
)

chart.show()