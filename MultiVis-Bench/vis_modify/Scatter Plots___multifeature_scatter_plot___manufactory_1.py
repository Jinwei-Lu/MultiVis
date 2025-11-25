import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/manufactory_1.sqlite')
query = '''
SELECT 
    M.Revenue AS Revenue,
    AVG(P.Price) AS AvgProductPrice,
    COUNT(P.Code) AS ProductCount,
    M.Headquarter AS Headquarter
FROM 
    Manufacturers AS M
JOIN 
    Products AS P ON M.Code = P.Manufacturer
GROUP BY 
    M.Code
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_circle().encode(
    alt.X('Revenue').scale(zero=False).title('Manufacturer Revenue'),
    alt.Y('AvgProductPrice').scale(zero=False, padding=1).title('Average Product Price'),
    color='Headquarter',
    size='ProductCount'
).properties(
    title='Manufacturer Revenue vs. Average Product Price'
)

chart.show()