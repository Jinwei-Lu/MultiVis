import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/journal_committee.sqlite')

query = '''
SELECT Theme, SUM(Sales) AS Total_Sales
FROM journal
GROUP BY Theme
ORDER BY Total_Sales DESC
'''

df = pd.read_sql_query(query, conn)
conn.close()

threshold = 2000

bars = alt.Chart(df).mark_bar(color="steelblue").encode(
    x=alt.X("Theme:N", title="Journal Theme"),
    y=alt.Y("Total_Sales:Q", title="Total Sales")
)

highlight = bars.mark_bar(color="#e45755").encode(
    y2=alt.Y2(datum=threshold)
).transform_filter(
    alt.datum.Total_Sales > threshold
)

rule = alt.Chart().mark_rule(color="black", strokeDash=[3, 5]).encode(
    y=alt.Y(datum=threshold)
)

label = rule.mark_text(
    x="width",
    dx=-2,
    align="right",
    baseline="bottom",
    text="High Sales Threshold"
)

chart = (bars + highlight + rule + label).properties(
    title="Journal Sales by Theme with Highlighted High Performers"
)

chart.show()