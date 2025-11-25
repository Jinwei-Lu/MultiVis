import altair as alt
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/journal_committee.sqlite')
query = '''
SELECT
    e.Age,
    j.Sales,
    jc.Work_Type
FROM
    editor AS e
JOIN
    journal_committee AS jc ON e.Editor_ID = jc.Editor_ID
JOIN
    journal AS j ON jc.Journal_ID = j.Journal_ID;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df)
base_bar = base.mark_bar(opacity=0.3, binSpacing=0)

xscale = alt.Scale(domain=(df['Age'].min() - 1, df['Age'].max() + 1))
yscale = alt.Scale(domain=(df['Sales'].min() - 100, df['Sales'].max() + 100))

points = base.mark_circle().encode(
    alt.X("Age:Q").scale(xscale),
    alt.Y("Sales:Q").scale(yscale),
    color="Work_Type:N",
)

top_hist = (
    base_bar
    .encode(
        alt.X("Age:Q")
            .bin(maxbins=20, extent=xscale.domain).stack(None).title(""),
        alt.Y("count()").stack(None).title(""),
        alt.Color("Work_Type:N"),
    )
    .properties(height=60)
)

right_hist = (
    base_bar
    .encode(
        alt.Y("Sales:Q")
            .bin(maxbins=20, extent=yscale.domain)
            .stack(None)
            .title(""),
        alt.X("count()").stack(None).title(""),
        alt.Color("Work_Type:N"),
    )
    .properties(width=60)
)

chart = top_hist & (points | right_hist)

chart