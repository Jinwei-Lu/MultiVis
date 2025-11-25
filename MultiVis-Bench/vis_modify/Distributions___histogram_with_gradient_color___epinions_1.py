import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/epinions_1.sqlite')
query = '''
SELECT trust
FROM trust
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    alt.X("trust:Q").bin(maxbins=20).scale(domain=[0, 10]),
    alt.Y('count()'),
    alt.Color("trust:Q").bin(maxbins=20).scale(scheme='pinkyellowgreen')
)

chart.show()