import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/dog_kennels.sqlite')
query = """
SELECT
    STRFTIME('%Y-%m', date_of_treatment) AS treatment_month,
    SUM(cost_of_treatment) AS monthly_cost
FROM Treatments
GROUP BY treatment_month
ORDER BY treatment_month;
"""
df = pd.read_sql_query(query, conn)
conn.close()

data = []
total_cost = 0
data.append({"label": "Start", "amount": 0})

for index, row in df.iterrows():
    amount = row['monthly_cost']
    total_cost += amount
    data.append({"label": row['treatment_month'], "amount": amount})

data.append({"label": "End", "amount": 0})

source = pd.DataFrame(data)
amount = alt.datum.amount
label = alt.datum.label
window_lead_label = alt.datum.window_lead_label
window_sum_amount = alt.datum.window_sum_amount

calc_prev_sum = alt.expr.if_(label == "End", 0, window_sum_amount - amount)
calc_amount = alt.expr.if_(label == "End", window_sum_amount, amount)
calc_text_amount = (
    alt.expr.if_((label != "Start") & (label != "End") & calc_amount > 0, "+", "")
    + calc_amount
)

base_chart = alt.Chart(source).transform_window(
    window_sum_amount="sum(amount)",
    window_lead_label="lead(label)",
).transform_calculate(
    calc_lead=alt.expr.if_((window_lead_label == None), label, window_lead_label),
    calc_prev_sum=calc_prev_sum,
    calc_amount=calc_amount,
    calc_text_amount=calc_text_amount,
    calc_center=(window_sum_amount + calc_prev_sum) / 2,
    calc_sum_dec=alt.expr.if_(window_sum_amount < calc_prev_sum, window_sum_amount, ""),
    calc_sum_inc=alt.expr.if_(window_sum_amount > calc_prev_sum, window_sum_amount, ""),
).encode(
    x=alt.X("label:O", axis=alt.Axis(title="Months", labelAngle=45), sort=None)
)

color_coding = (
    alt.when((label == "Start") | (label == "End"))
    .then(alt.value("#878d96"))
    .when(calc_amount < 0)
    .then(alt.value("#24a148"))
    .otherwise(alt.value("#fa4d56"))
)

bar = base_chart.mark_bar(size=45).encode(
    y=alt.Y("calc_prev_sum:Q", title="Cost of Treatment"),
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