import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/gymnast.sqlite')
query = '''
SELECT 
    Floor_Exercise_Points AS Floor,
    Pommel_Horse_Points AS Pommel_Horse,
    Rings_Points AS Rings,
    Vault_Points AS Vault,
    Parallel_Bars_Points AS Parallel_Bars,
    Horizontal_Bar_Points AS Horizontal_Bar
FROM gymnast
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).transform_fold(
    ["Floor", "Pommel_Horse", "Rings", "Vault", "Parallel_Bars", "Horizontal_Bar"],
    as_=["Event", "Score"]
).transform_density(
    density="Score",
    bandwidth=0.1,
    groupby=["Event"],
    extent=[8, 10]
).mark_area().encode(
    alt.X("value:Q", title="Score"),
    alt.Y("density:Q", title="Density"),
    alt.Row("Event:N")
).properties(
    width=300, height=50
)

chart.show()