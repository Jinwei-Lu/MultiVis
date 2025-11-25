import altair as alt
import pandas as pd

data = {
    'Origin': ['USA', 'Europe', 'Japan', 'USA', 'Europe', 'Japan', 'USA', 'Europe', 'Japan'],
    'Cylinders': [4, 4, 4, 6, 6, 6, 8, 8, 8],
    'mean_horsepower': [80, 75, 70, 110, 105, 100, 180, 170, 160]
}
source = pd.DataFrame(data)

source['Origin'] = pd.Categorical(source['Origin'], categories=['USA', 'Europe', 'Japan'], ordered=True)
source['Cylinders'] = pd.Categorical(source['Cylinders'], categories=[4, 6, 8], ordered=True)

base = alt.Chart(source).encode(
    alt.X('Cylinders:O', sort=None),
    alt.Y('Origin:O', sort=None),
)

heatmap = base.mark_rect().encode(
    alt.Color('mean_horsepower:Q')
)

color = (
    alt.condition(alt.datum.mean_horsepower > 150,
                  alt.value("black"),
                  alt.value("white"))
)

text = base.mark_text(baseline='middle').encode(
    alt.Text('mean_horsepower:Q', format=".0f"), color=color
)

chart = heatmap + text

chart