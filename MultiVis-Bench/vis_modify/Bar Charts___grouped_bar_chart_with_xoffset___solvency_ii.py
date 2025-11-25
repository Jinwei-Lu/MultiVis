import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/solvency_ii.sqlite')

query = '''
SELECT 
    E.Event_Type_Code AS EventType,
    P.Product_Type_Code AS ProductType,
    COUNT(PE.Product_ID) AS ProductCount
FROM 
    Events AS E
JOIN 
    Products_in_Events AS PE ON E.Event_ID = PE.Event_ID
JOIN 
    Products AS P ON PE.Product_ID = P.Product_ID
GROUP BY 
    E.Event_Type_Code, P.Product_Type_Code
ORDER BY 
    E.Event_Type_Code, P.Product_Type_Code;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("EventType:N", title="Event Type"),
    y=alt.Y("ProductCount:Q", title="Total Number of Products"),
    xOffset="ProductType:N",
    color="ProductType:N"
).properties(
    title="Total Products by Event Type and Product Type"
)

chart.show()