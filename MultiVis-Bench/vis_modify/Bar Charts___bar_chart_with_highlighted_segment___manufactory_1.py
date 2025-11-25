import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/manufactory_1.sqlite')
query = '''
SELECT Name, Revenue
FROM Manufacturers
'''
df = pd.read_sql_query(query, conn)
conn.close()

threshold_value = 100
threshold_df = pd.DataFrame([{"threshold": threshold_value}])

bars = alt.Chart(df).mark_bar().encode(
    x=alt.X("Name:N", title="Manufacturer"),
    y=alt.Y("Revenue:Q", title="Revenue (in billions)")
)

highlight = alt.Chart(df).mark_bar(color="#e45755").encode(
    x=alt.X("Name:N", title="Manufacturer"),
    y=alt.Y("baseline:Q", title="Revenue (in billions)"),
    y2=alt.Y2("Revenue:Q")
).transform_filter(
    alt.datum.Revenue > threshold_value
).transform_calculate(
    baseline=f"{threshold_value}"
)

rule = alt.Chart(threshold_df).mark_rule(color="black", strokeDash=[3, 5]).encode(
    y="threshold:Q"
)

chart = (bars + highlight + rule).properties(width=600, title="Manufacturer Revenue with Highlighted Threshold")

chart