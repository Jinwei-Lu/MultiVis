import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime

conn = sqlite3.connect('database/chinook_1.sqlite')

query = '''
SELECT 
    EmployeeId,
    FirstName || ' ' || LastName AS FullName,
    HireDate
FROM 
    Employee
'''

df = pd.read_sql_query(query, conn)

conn.close()

today = datetime.today()
df['start'] = df['HireDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').year)
df['end'] = today.year

chart = alt.Chart(df).mark_bar().encode(
    x='start:O',
    x2='end:O',
    y=alt.Y('FullName:N', title="Employee Name")
).properties(
    title="Employee Tenure at the Company"
)

chart