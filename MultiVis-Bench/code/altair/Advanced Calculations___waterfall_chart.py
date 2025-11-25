import altair as alt
import pandas as pd

data = [
    {"label": "Begin", "amount": 5000},
    {"label": "Q1", "amount": 2500},
    {"label": "Q2", "amount": -1000},
    {"label": "Q3", "amount": 3000},
    {"label": "Q4", "amount": -1500},
    {"label": "End", "amount": 0},
]

source = pd.DataFrame(data)

amount = alt.datum.amount
label = alt.datum.label
window_lead_label = alt.datum.window_lead_label
window_sum_amount = alt.datum.window_sum_amount

calc_prev_sum = alt.expr.if_(label == "End", 0, window_sum_amount - amount)
calc_amount = alt.expr.if_(label == "End", window_sum_amount, amount)
calc_text_amount = (
    alt.expr.if_((label != "Begin") & (label != "End") & calc_amount > 0, "+", "")
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
    x=alt.X("label:O", sort=None)
)

color_coding = (
    alt.when((label == "Begin") | (label == "End"))
    .then(alt.value("#878d96"))
    .when(calc_amount < 0)
    .then(alt.value("#24a148"))
    .otherwise(alt.value("#fa4d56"))
)

bar = base_chart.mark_bar().encode(
    y=alt.Y("calc_prev_sum:Q"),
    y2=alt.Y2("window_sum_amount:Q"),
    color=color_coding,
)

rule = base_chart.mark_rule().encode(
    y="window_sum_amount:Q",
    x2="calc_lead",
)

text_pos_values_top_of_bar = base_chart.mark_text().encode(
    text=alt.Text("calc_sum_inc:N"),
    y="calc_sum_inc:Q",
)
text_neg_values_bot_of_bar = base_chart.mark_text().encode(
    text=alt.Text("calc_sum_dec:N"),
    y="calc_sum_dec:Q",
)
text_bar_values_mid_of_bar = base_chart.mark_text().encode(
    text=alt.Text("calc_text_amount:N"),
    y="calc_center:Q",
)

alt.layer(
    bar,
    rule,
    text_pos_values_top_of_bar,
    text_neg_values_bot_of_bar,
    text_bar_values_mid_of_bar
)