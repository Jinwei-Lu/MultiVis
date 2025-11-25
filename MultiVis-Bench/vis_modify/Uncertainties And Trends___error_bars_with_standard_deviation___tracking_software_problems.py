import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/tracking_software_problems.sqlite')

query = '''
SELECT
    PCC.problem_category_description AS variety,
    STRFTIME('%J', P.date_problem_closed) - STRFTIME('%J', P.date_problem_reported) AS yield
FROM Problems AS P
JOIN Problem_Log AS PL
    ON P.problem_id = PL.problem_id
JOIN Problem_Category_Codes AS PCC
    ON PL.problem_category_code = PCC.problem_category_code
WHERE
    P.date_problem_closed IS NOT NULL AND P.date_problem_reported IS NOT NULL
'''

df = pd.read_sql_query(query, conn)
conn.close()

error_bars = alt.Chart(df).mark_errorbar(extent='stdev').encode(
  x=alt.X('yield:Q', scale=alt.Scale(zero=False), title='Days to Close Problem'),
  y=alt.Y('variety:N', title='Problem Category')
)

points = alt.Chart(df).mark_point(filled=True, color='black').encode(
  x=alt.X('mean(yield):Q', title='Days to Close Problem'),
  y=alt.Y('variety:N'),
)

error_bars + points