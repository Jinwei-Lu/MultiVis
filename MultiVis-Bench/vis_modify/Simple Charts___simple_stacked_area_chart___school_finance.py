import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/school_finance.sqlite')

query = '''
SELECT 
    S.School_name AS School,
    B.Year AS Year,
    SUM(B.Budgeted) AS Total_Budgeted,
    SUM(B.Invested) AS Total_Invested
FROM 
    budget AS B
JOIN 
    School AS S ON B.School_id = S.School_id
GROUP BY 
    S.School_name, B.Year
ORDER BY 
    B.Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

df_melted = df.melt(id_vars=['School', 'Year'], value_vars=['Total_Budgeted', 'Total_Invested'], 
                    var_name='Category', value_name='Amount')

chart = alt.Chart(df_melted).mark_area().encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Amount:Q", title="Amount"),
    color=alt.Color("School:N", title="School"),
    row=alt.Row("Category:N", title="Category")
).properties(
    width=600,
    height=150
)

chart.show()