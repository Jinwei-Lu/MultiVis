import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/dog_kennels.sqlite')

query = '''
SELECT 
    T1.treatment_type_description AS treatment_type,
    T2.cost_of_treatment AS cost
FROM 
    Treatment_Types AS T1
JOIN 
    Treatments AS T2
ON 
    T1.treatment_type_code = T2.treatment_type_code
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    alt.X("cost:Q").bin(),
    y="count()",
    row="treatment_type:N"
)

chart.show()