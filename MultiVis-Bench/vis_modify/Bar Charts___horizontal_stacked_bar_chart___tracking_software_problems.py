import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/tracking_software_problems.sqlite')

query = '''
SELECT 
    pcc.problem_category_description AS category,
    psc.problem_status_description AS status,
    COUNT(*) AS count
FROM 
    Problem_Log AS pl
JOIN 
    Problem_Category_Codes AS pcc ON pl.problem_category_code = pcc.problem_category_code
JOIN 
    Problem_Status_Codes AS psc ON pl.problem_status_code = psc.problem_status_code
GROUP BY 
    pcc.problem_category_description, psc.problem_status_description
ORDER BY 
    pcc.problem_category_description, psc.problem_status_description;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='sum(count):Q',
    y='category:N',
    color='status:N'
).properties(
    title="Problem Distribution by Category and Status"
)

chart