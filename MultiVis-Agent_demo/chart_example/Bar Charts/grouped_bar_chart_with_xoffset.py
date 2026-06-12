import altair as alt
import pandas as pd

source = pd.DataFrame({
    "Category":list("AAABBBCCC"),
    "Group":list("xyzxyzxyz"),
    "Value":[0.1, 0.6, 0.9, 0.7, 0.2, 1.1, 0.6, 0.1, 0.2]
})

chart = alt.Chart(source).mark_bar().encode(
    x=alt.X("Category:N"),
    y=alt.Y("Value:Q"),
    xOffset=alt.XOffset("Group:N")
)

chart