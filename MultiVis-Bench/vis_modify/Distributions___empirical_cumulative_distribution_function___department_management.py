import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/department_management.sqlite')
query = '''
SELECT Budget_in_Billions
FROM department
'''
df = pd.read_sql_query(query, conn)
conn.close()

ecdf_chart = alt.Chart(df).transform_window(
    ecdf="cume_dist()",
    sort=[{"field": "Budget_in_Billions"}]
).mark_line(interpolate='step-after').encode(
    x=alt.X("Budget_in_Billions:Q", title="Budget in Billions"),
    y=alt.Y("ecdf:Q", title="Cumulative Proportion", scale=alt.Scale(domain=[0, 1]))
).properties(
    title="Empirical Cumulative Distribution of Department Budgets",
    width=600,
    height=400
)

ecdf_chart