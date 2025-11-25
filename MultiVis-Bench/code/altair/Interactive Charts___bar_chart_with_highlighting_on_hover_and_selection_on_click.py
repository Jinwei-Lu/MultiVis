import altair as alt

source = {
    "values": [
        {"a": "Jan", "b": 22},
        {"a": "Feb", "b": 35},
        {"a": "Mar", "b": 48},
        {"a": "Apr", "b": 55},
        {"a": "May", "b": 62},
        {"a": "Jun", "b": 70},
        {"a": "Jul", "b": 78},
        {"a": "Aug", "b": 75},
        {"a": "Sep", "b": 68},
        {"a": "Oct", "b": 55},
        {"a": "Nov", "b": 40},
        {"a": "Dec", "b": 28},
    ]
}

select = alt.selection_point(name="select", on="click")
highlight = alt.selection_point(name="highlight", on="pointerover", empty=False)

stroke_width = (
    alt.when(select).then(alt.value(2, empty=False))
    .when(highlight).then(alt.value(1))
    .otherwise(alt.value(0))
)

alt.Chart(source).mark_bar().encode(
    x="a:O",
    y="b:Q",
    fillOpacity=alt.when(select).then(alt.value(1)).otherwise(alt.value(0.3)),
    strokeWidth=stroke_width,
).add_params(select, highlight)