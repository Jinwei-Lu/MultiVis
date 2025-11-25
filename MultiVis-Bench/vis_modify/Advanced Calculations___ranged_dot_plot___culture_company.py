import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/culture_company.sqlite')

query = '''
SELECT Title, Budget_million, Gross_worldwide
FROM movie
'''

df = pd.read_sql_query(query, conn)
conn.close()

df_melted = pd.melt(df, id_vars=['Title'], value_vars=['Budget_million', 'Gross_worldwide'], var_name='Measure', value_name='Value')

chart = alt.Chart(df_melted).mark_line(color="#db646f").encode(
    y=alt.Y('Title:N'),
    x=alt.X('Value:Q'),
    detail='Title:N'
)

points = alt.Chart(df_melted).mark_point(
    size=100,
    opacity=1,
    filled=True,
).encode(
    y=alt.Y('Title:N'),
    x=alt.X('Value:Q'),
    color=alt.Color('Measure:N').scale(domain=['Budget_million', 'Gross_worldwide'], range=["#e6959c", "#911a24"])
)

final_chart = (chart + points)
final_chart