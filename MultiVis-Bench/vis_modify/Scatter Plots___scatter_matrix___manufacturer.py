import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/manufacturer.sqlite')

query = '''
SELECT Manufacturer_ID, Open_Year, Num_of_Factories, Num_of_Shops, Name
FROM manufacturer
'''

df = pd.read_sql_query(query, conn)
conn.close()

scatter_matrix = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y(alt.repeat("row"), type='quantitative'),
    color='Name:N'
).properties(
    width=150,
    height=150
).repeat(
    row=['Num_of_Factories', 'Num_of_Shops', 'Open_Year'],
    column=['Open_Year', 'Num_of_Shops', 'Num_of_Factories']
).interactive()

scatter_matrix