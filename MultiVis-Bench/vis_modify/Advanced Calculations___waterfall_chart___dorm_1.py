import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/dorm_1.sqlite')

query = '''
SELECT dorm_name, student_capacity
FROM Dorm
ORDER BY student_capacity;
'''

df_dorm = pd.read_sql_query(query, conn)
conn.close()

data = []
data.append({"label": "Start", "amount": 0})
for index, row in df_dorm.iterrows():
    data.append({"label": row['dorm_name'], "amount": row['student_capacity']})
total_capacity = df_dorm['student_capacity'].sum()
data.append({"label": "Total", "amount": total_capacity})

source = pd.DataFrame(data)

amount = alt.datum.amount
label = alt.datum.label
window_lead_label = alt.datum.window_lead_label
window_sum_amount = alt.datum.window_sum_amount

calc_prev_sum = alt.expr.if_(label == "Total", 0, window_sum_amount - amount)
calc_amount = alt.expr.if_(label == "Total", window_sum_amount, amount)
calc_text_amount = (
    alt.expr.if_((label != "Start") & (label != "Total") & calc_amount > 0, "+", "")
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
    x=alt.X("label:O", axis=alt.Axis(title="Dormitory", labelAngle=45), sort=None)
)

color_coding = (
    alt.when((label == "Start") | (label == "Total"))
    .then(alt.value("#878d96"))
    .when(calc_amount < 0)
    .then(alt.value("#24a148"))
    .otherwise(alt.value("#fa4d56"))
)

bar = base_chart.mark_bar(size=45).encode(
    y=alt.Y("calc_prev_sum:Q", title="Student Capacity"),
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

chart = alt.layer(
    bar,
    rule,
    text_pos_values_top_of_bar,
    text_neg_values_bot_of_bar,
    text_bar_values_mid_of_bar
).properties(
    title='Cumulative Student Capacity Across Dormitories',
    width=800,
    height=450
)

chart