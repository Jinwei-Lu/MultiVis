import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/pets_1.sqlite')
query = '''
SELECT pet_age, weight, PetID
FROM Pets
'''
df = pd.read_sql_query(query, conn)
conn.close()
df['PetID'] = df['PetID'].astype(str)

points = alt.Chart(df).mark_point().encode(
    x='pet_age:Q',
    y='weight:Q'
)

text = points.mark_text(
    align='left',
    baseline='middle',
    dx=7
).encode(
    text='PetID:N'
)

points + text