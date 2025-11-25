import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/document_management.sqlite')

query = '''
SELECT 
    document_type_code AS Document_Type,
    access_count AS Access_Count
FROM 
    Documents
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df).mark_bar().encode(
    alt.X("Access_Count:Q").bin(maxbins=30),
    y="count()",
    row="Document_Type"
)

chart