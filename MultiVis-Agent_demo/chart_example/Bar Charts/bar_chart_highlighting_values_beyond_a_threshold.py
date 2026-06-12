import pandas as pd
import altair as alt

days = list(range(1, 16))
values = [55, 112, 65, 38, 80, 138, 120, 103, 395, 200, 72, 51, 112, 175, 131]
threshold = 300

source_df = pd.DataFrame({
    "Day": days,
    "Value": values
})

bars = alt.Chart(source_df).mark_bar().encode(
    x="Day:O",
    y="Value:Q"
)

highlight = alt.Chart(source_df).mark_bar().encode(
    x="Day:O",
    y="Value:Q",
    y2=alt.Y2(datum=threshold)
).transform_filter(
    alt.datum.Value > threshold
)

rule = alt.Chart(pd.DataFrame({'y': [threshold]})).mark_rule().encode(
    y=alt.Y('y:Q')
)

label = alt.Chart(pd.DataFrame({'y': [threshold]})).mark_text(
    text='hazardous'
).encode(
    y=alt.Y('y:Q')
)

chart = (bars + highlight + rule + label)

chart