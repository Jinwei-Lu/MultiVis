import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/department_store.sqlite')

query = '''
SELECT 
    P.product_name AS product,
    COUNT(OI.order_item_id) AS purchase_count
FROM 
    Products AS P
JOIN 
    Order_Items AS OI ON P.product_id = OI.product_id
GROUP BY 
    P.product_name
ORDER BY 
    purchase_count DESC
LIMIT 10;
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df).mark_bar().encode(
    y=alt.Y('product:N', sort='-x', title='Product'),
    x=alt.X('purchase_count:Q', title='Purchase Count')
).properties(
    title='Top 10 Most Frequently Purchased Products'
)

chart.show()