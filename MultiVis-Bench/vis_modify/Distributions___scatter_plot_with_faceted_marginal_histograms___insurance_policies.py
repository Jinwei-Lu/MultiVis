import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/insurance_policies.sqlite')

query = '''
SELECT
    C.Amount_Claimed,
    C.Amount_Settled,
    CP.Policy_Type_Code
FROM
    Claims AS C
JOIN
    Customer_Policies AS CP ON C.Policy_ID = CP.Policy_ID
'''

df = pd.read_sql_query(query, conn)

conn.close()

base = alt.Chart(df)
base_bar = base.mark_bar(opacity=0.3, binSpacing=0)

points = base.mark_circle().encode(
    alt.X("Amount_Claimed:Q"),
    alt.Y("Amount_Settled:Q"),
    color="Policy_Type_Code:N",
)

top_hist = (
    base_bar
    .encode(
        alt.X("Amount_Claimed:Q")
            .bin(maxbins=20).stack(None).title(""),
        alt.Y("count()").stack(None).title(""),
        alt.Color("Policy_Type_Code:N"),
    )
    .properties(height=60)
)

right_hist = (
    base_bar
    .encode(
        alt.Y("Amount_Settled:Q")
            .bin(maxbins=20)
            .stack(None)
            .title(""),
        alt.X("count()").stack(None).title(""),
        alt.Color("Policy_Type_Code:N"),
    )
    .properties(width=60)
)

chart = top_hist & (points | right_hist)
chart