import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/local_govt_mdm.sqlite')

query = '''
SELECT 
    source_system_code, 
    COUNT(master_customer_id) AS customer_count
FROM 
    CMI_Cross_References
GROUP BY 
    source_system_code
'''

df = pd.read_sql_query(query, conn)
conn.close()

color = alt.condition(
    alt.datum.source_system_code == 'Rent',
    alt.value('orange'),
    alt.value('steelblue')
)

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('source_system_code:N', title='Source System'),
    y=alt.Y('customer_count:Q', title='Number of Customers'),
    color=color
).properties(
    width=600,
    title='Number of Customers by Source System'
)

chart