import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/poker_player.sqlite')
query = '''
SELECT Final_Table_Made, Best_Finish, Earnings
FROM poker_player;
'''
df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval(encodings=['x'])

base = alt.Chart(df, width=160, height=130).mark_bar().encode(
    alt.X(alt.repeat('column'), bin=alt.Bin(maxbins=20)),
    y='count()',
)

background = base.encode(
    color=alt.value('#ddd')
).add_params(brush)

highlight = base.transform_filter(brush)

chart = alt.layer(
    background,
    highlight
).repeat(column=["Final_Table_Made", "Best_Finish", "Earnings"])

chart