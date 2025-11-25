import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/gymnast.sqlite')

query = '''
SELECT 
    Gymnast_ID,
    Floor_Exercise_Points AS Floor,
    Pommel_Horse_Points AS Pommel_Horse,
    Rings_Points AS Rings,
    Vault_Points AS Vault,
    Parallel_Bars_Points AS Parallel_Bars,
    Horizontal_Bar_Points AS Horizontal_Bar
FROM 
    gymnast
'''

df = pd.read_sql_query(query, conn)

conn.close()

df_long = df.melt(id_vars=['Gymnast_ID'], 
                  value_vars=['Floor', 'Pommel_Horse', 'Rings', 'Vault', 'Parallel_Bars', 'Horizontal_Bar'],
                  var_name='Event', value_name='Points')

chart = alt.Chart(df_long).mark_area().encode(
    x=alt.X("Gymnast_ID:N", title="Gymnast ID"),
    y=alt.Y("Points:Q").stack("normalize"),
    color="Event:N"
).properties(
    title="Normalized Distribution of Points Across Gymnastic Events"
)

chart.show()