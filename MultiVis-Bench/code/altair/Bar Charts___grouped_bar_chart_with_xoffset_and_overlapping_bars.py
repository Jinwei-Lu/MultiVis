import altair as alt
import pandas as pd

new_source = pd.DataFrame({
    'category': list('XXYYZZ'),
    'group':    list('abcabc'),
    'value':    [0.8, 0.2, 0.5, 0.9, 0.3, 0.7]
})

base = alt.Chart(new_source).encode(
    x="category:N",
    y="value:Q",
    xOffset=alt.XOffset("group:N")
)

alt.layer(
    base.mark_bar().encode(fill="group:N"),
    base.mark_text().encode(text="value:Q"),
)