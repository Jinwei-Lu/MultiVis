import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/loan_1.sqlite')

query = '''
SELECT branch_ID, bname, no_of_customers
FROM bank
'''

df = pd.read_sql_query(query, conn)
conn.close()

threshold = 300

bars = alt.Chart(df).mark_bar(color="steelblue").encode(
    x=alt.X("bname:N", title="Branch Name"),
    y=alt.Y("no_of_customers:Q", title="Number of Customers"),
)

highlight = bars.mark_bar(color="#e45755").encode(
    y2=alt.Y2(datum=threshold)
).transform_filter(
    alt.datum.no_of_customers > threshold
)

rule = alt.Chart().mark_rule().encode(
    y=alt.Y(datum=threshold)
)

label = rule.mark_text(
    x="width",
    dx=-2,
    align="right",
    baseline="bottom",
    text="Threshold (300)"
)

chart = (bars + highlight + rule + label).properties(
    title="Branches with More Than 300 Customers"
)

chart