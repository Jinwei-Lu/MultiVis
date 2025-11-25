import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/loan_1.sqlite')

query = '''
SELECT c.no_of_loans, c.credit_score, c.state
FROM customer AS c
WHERE c.no_of_loans IS NOT NULL AND c.credit_score IS NOT NULL
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df, width=100, height=100).mark_point().encode(
    x="no_of_loans:Q",
    y="credit_score:Q",
    row="state:N"
)

chart