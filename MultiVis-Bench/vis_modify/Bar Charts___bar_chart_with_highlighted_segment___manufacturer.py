import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/manufacturer.sqlite')

query = '''
SELECT Name, Num_of_Factories
FROM manufacturer
'''

df = pd.read_sql_query(query, conn)

conn.close()

threshold_value = 20
threshold_df = pd.DataFrame([{"threshold": threshold_value}])

bars = alt.Chart(df).mark_bar().encode(
    x=alt.X('Name:N', title='Manufacturer'),
    y=alt.Y('Num_of_Factories:Q', title='Number of Factories')
)

highlight = alt.Chart(df).mark_bar(color="#e45755").encode(
    x='Name:N',
    y='baseline:Q',
    y2='Num_of_Factories:Q'
).transform_filter(
    alt.datum.Num_of_Factories > threshold_value
).transform_calculate("baseline", str(threshold_value))

rule = alt.Chart(threshold_df).mark_rule(color="black", strokeDash=[3, 5]).encode(
    y='threshold:Q'
)

chart = (bars + highlight + rule).properties(width=600, title="Number of Factories by Manufacturer")

chart