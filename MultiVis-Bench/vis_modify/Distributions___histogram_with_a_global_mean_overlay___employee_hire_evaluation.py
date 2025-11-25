import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/employee_hire_evaluation.sqlite')
query = "SELECT Age FROM employee;"
df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df)
bar = base.mark_bar().encode(
    alt.X('Age:Q', bin=alt.Bin(maxbins=30), title='Employee Age'),
    y='count()',
    tooltip=['count()', 'Age']
)
rule = base.mark_rule(color='red').encode(
    x='mean(Age):Q',
    size=alt.value(5)
)
chart = bar + rule
chart