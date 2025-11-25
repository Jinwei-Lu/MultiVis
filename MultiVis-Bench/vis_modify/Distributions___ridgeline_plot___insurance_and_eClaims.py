import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/insurance_and_eClaims.sqlite')

query = '''
SELECT Claim_Status_Code, Amount_Claimed
FROM Claim_Headers
WHERE Amount_Claimed IS NOT NULL
'''

df = pd.read_sql_query(query, conn)
conn.close()

step = 20
overlap = 1

chart = alt.Chart(df, height=step).transform_density(
    'Amount_Claimed',
    groupby=['Claim_Status_Code'],
    as_=['Amount_Claimed', 'density'],
    extent=[0, df['Amount_Claimed'].max()],
    bandwidth=50
).mark_area(
    interpolate='monotone',
    fillOpacity=0.8,
    stroke='lightgray',
    strokeWidth=0.5
).encode(
    alt.X('Amount_Claimed:Q').title('Claim Amount'),
    alt.Y('density:Q')
        .axis(None)
        .scale(range=[step, -step * overlap]),
    alt.Fill('Claim_Status_Code:N')
        .legend(None)
        .scale(scheme='category10')
).facet(
    row=alt.Row('Claim_Status_Code:N')
        .title(None)
        .header(labelAngle=0, labelAlign='left')
).properties(
    title='Distribution of Claim Amounts by Claim Status',
    bounds='flush'
).configure_facet(
    spacing=0
).configure_view(
    stroke=None
).configure_title(
    anchor='end'
)

chart.show()