import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_and_eClaims.sqlite')

query = '''
SELECT 
    ch.Claim_Header_ID,
    ch.Amount_Claimed,
    ch.Amount_Piad AS Amount_Paid,
    ch.Claim_Type_Code,
    ch.Date_of_Settlement
FROM 
    Claim_Headers AS ch
WHERE 
    ch.Amount_Claimed IS NOT NULL AND ch.Amount_Piad IS NOT NULL
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval()

points = alt.Chart(df).mark_point().encode(
    x=alt.X('Amount_Claimed:Q', title='Amount Claimed'),
    y=alt.Y('Amount_Paid:Q', title='Amount Paid'),
    color=alt.condition(brush, alt.value("steelblue"), alt.value("grey")),
    tooltip=['Claim_Type_Code:N', 'Date_of_Settlement:T']
).add_params(brush).properties(
    width=400,
    height=400
)

ranked_text = alt.Chart(df).mark_text(align='right').encode(
    y=alt.Y('row_number:O').axis(None)
).transform_filter(
    brush
).transform_window(
    row_number='row_number()'
).transform_filter(
    alt.datum.row_number < 15
)

claim_type = ranked_text.encode(text='Claim_Type_Code:N').properties(
    title=alt.Title(text='Claim Type', align='right')
)
settlement_date = ranked_text.encode(text='Date_of_Settlement:T').properties(
    title=alt.Title(text='Settlement Date', align='right')
)
text = alt.hconcat(claim_type, settlement_date)

chart = alt.hconcat(
    points,
    text
).resolve_legend(
    color="independent"
).configure_view(
    stroke=None
)

chart.show()