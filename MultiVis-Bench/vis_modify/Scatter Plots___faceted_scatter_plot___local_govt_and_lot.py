import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/local_govt_and_lot.sqlite')

query = '''
SELECT 
    T1.service_type_code AS Service_Type,
    COUNT(T2.resident_id) AS Resident_Count,
    T3.property_type_code AS Property_Type
FROM 
    Services AS T1
JOIN 
    Residents_Services AS T2 ON T1.service_id = T2.service_id
JOIN 
    Properties AS T3 ON T2.property_id = T3.property_id
WHERE 
    T1.service_details = 'Satisfied'
GROUP BY 
    T1.service_type_code, T3.property_type_code
ORDER BY 
    T1.service_type_code, T3.property_type_code;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df, width=100, height=100).mark_point().encode(
    x="Resident_Count:Q",
    y="Service_Type:N",
    row="Property_Type:N"
)

chart