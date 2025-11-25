import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/document_management.sqlite')

query = '''
SELECT 
    DS.document_structure_description,
    SUM(D.access_count) AS total_access_count
FROM Documents AS D
JOIN Document_Structures AS DS 
    ON D.document_structure_code = DS.document_structure_code
GROUP BY DS.document_structure_description
ORDER BY DS.document_structure_code
'''

df = pd.read_sql_query(query, conn)
conn.close()

begin_row = pd.DataFrame([{"document_structure_description": "Begin", "total_access_count": 0}])
end_row = pd.DataFrame([{"document_structure_description": "End", "total_access_count": df['total_access_count'].sum()}])
df = pd.concat([begin_row, df, end_row], ignore_index=True)

amount = alt.datum.total_access_count
label = alt.datum.document_structure_description
window_lead_label = alt.datum.window_lead_label
window_sum_amount = alt.datum.window_sum_amount

calc_prev_sum = alt.expr.if_(label == "End", 0, window_sum_amount - amount)
calc_amount = alt.expr.if_(label == "End", window_sum_amount, amount)
calc_text_amount = (
    alt.expr.if_((label != "Begin") & (label != "End") & calc_amount > 0, "+", "")
    + calc_amount
)

base_chart = alt.Chart(df).transform_window(
    window_sum_amount="sum(total_access_count)",
    window_lead_label="lead(document_structure_description)",
).transform_calculate(
    calc_lead=alt.expr.if_((window_lead_label == None), label, window_lead_label),
    calc_prev_sum=calc_prev_sum,
    calc_amount=calc_amount,
    calc_text_amount=calc_text_amount,
    calc_center=(window_sum_amount + calc_prev_sum) / 2,
    calc_sum_dec=alt.expr.if_(window_sum_amount < calc_prev_sum, window_sum_amount, ""),
    calc_sum_inc=alt.expr.if_(window_sum_amount > calc_prev_sum, window_sum_amount, ""),
).encode(
    x=alt.X("document_structure_description:O", axis=alt.Axis(title="Document Structure", labelAngle=0), sort=None)
)

color_coding = (
    alt.when((label == "Begin") | (label == "End"))
    .then(alt.value("#878d96"))
    .when(calc_amount < 0)
    .then(alt.value("#24a148"))
    .otherwise(alt.value("#fa4d56"))
)

bar = base_chart.mark_bar(size=45).encode(
    y=alt.Y("calc_prev_sum:Q", title="Access Count"),
    y2=alt.Y2("window_sum_amount:Q"),
    color=color_coding,
)

rule = base_chart.mark_rule(xOffset=-22.5, x2Offset=22.5).encode(
    y="window_sum_amount:Q",
    x2="calc_lead",
)

text_pos_values_top_of_bar = base_chart.mark_text(baseline="bottom", dy=-4).encode(
    text=alt.Text("calc_sum_inc:N"),
    y="calc_sum_inc:Q",
)
text_neg_values_bot_of_bar = base_chart.mark_text(baseline="top", dy=4).encode(
    text=alt.Text("calc_sum_dec:N"),
    y="calc_sum_dec:Q",
)
text_bar_values_mid_of_bar = base_chart.mark_text(baseline="middle").encode(
    text=alt.Text("calc_text_amount:N"),
    y="calc_center:Q",
    color=alt.value("white"),
)

alt.layer(
    bar,
    rule,
    text_pos_values_top_of_bar,
    text_neg_values_bot_of_bar,
    text_bar_values_mid_of_bar
).properties(
    width=800,
    height=450
)