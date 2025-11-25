import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/cre_Doc_Tracking_DB.sqlite')

query = '''
SELECT 
    T1.Document_Type_Name,
    (julianday(T2.Date_Stored) - julianday(T3.Date_in_Location_From)) AS Storage_Duration
FROM 
    Ref_Document_Types AS T1
JOIN 
    All_Documents AS T2 ON T1.Document_Type_Code = T2.Document_Type_Code
JOIN 
    Document_Locations AS T3 ON T2.Document_ID = T3.Document_ID
WHERE 
    T3.Date_in_Location_From IS NOT NULL AND T2.Date_Stored IS NOT NULL
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_boxplot(extent='min-max').encode(
    x=alt.X('Document_Type_Name:N', title='Document Type'),
    y=alt.Y('Storage_Duration:Q', title='Storage Duration (Days)')
)

chart