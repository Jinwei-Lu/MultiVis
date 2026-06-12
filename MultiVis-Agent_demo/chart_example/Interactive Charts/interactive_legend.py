import altair as alt
import pandas as pd

data_list = [
    {'date': '2000-01-01', 'series': 'Agriculture', 'count': 150},
    {'date': '2000-01-01', 'series': 'Construction', 'count': 220},
    {'date': '2000-01-01', 'series': 'Manufacturing', 'count': 350},
    {'date': '2000-02-01', 'series': 'Agriculture', 'count': 160},
    {'date': '2000-02-01', 'series': 'Construction', 'count': 230},
    {'date': '2000-02-01', 'series': 'Manufacturing', 'count': 340},
    {'date': '2000-03-01', 'series': 'Agriculture', 'count': 170},
    {'date': '2000-03-01', 'series': 'Construction', 'count': 240},
    {'date': '2000-03-01', 'series': 'Manufacturing', 'count': 330},
    {'date': '2000-04-01', 'series': 'Agriculture', 'count': 180},
    {'date': '2000-04-01', 'series': 'Construction', 'count': 250},
    {'date': '2000-04-01', 'series': 'Manufacturing', 'count': 320},
    {'date': '2000-05-01', 'series': 'Agriculture', 'count': 190},
    {'date': '2000-05-01', 'series': 'Construction', 'count': 260},
    {'date': '2000-05-01', 'series': 'Manufacturing', 'count': 310},
    {'date': '2000-06-01', 'series': 'Agriculture', 'count': 200},
    {'date': '2000-06-01', 'series': 'Construction', 'count': 270},
    {'date': '2000-06-01', 'series': 'Manufacturing', 'count': 300},
    {'date': '2000-07-01', 'series': 'Agriculture', 'count': 210},
    {'date': '2000-07-01', 'series': 'Construction', 'count': 280},
    {'date': '2000-07-01', 'series': 'Manufacturing', 'count': 290},
    {'date': '2000-08-01', 'series': 'Agriculture', 'count': 220},
    {'date': '2000-08-01', 'series': 'Construction', 'count': 290},
    {'date': '2000-08-01', 'series': 'Manufacturing', 'count': 280},
    {'date': '2000-09-01', 'series': 'Agriculture', 'count': 230},
    {'date': '2000-09-01', 'series': 'Construction', 'count': 300},
    {'date': '2000-09-01', 'series': 'Manufacturing', 'count': 270},
    {'date': '2000-10-01', 'series': 'Agriculture', 'count': 240},
    {'date': '2000-10-01', 'series': 'Construction', 'count': 310},
    {'date': '2000-10-01', 'series': 'Manufacturing', 'count': 260},
    {'date': '2000-11-01', 'series': 'Agriculture', 'count': 250},
    {'date': '2000-11-01', 'series': 'Construction', 'count': 320},
    {'date': '2000-11-01', 'series': 'Manufacturing', 'count': 250},
    {'date': '2000-12-01', 'series': 'Agriculture', 'count': 260},
    {'date': '2000-12-01', 'series': 'Construction', 'count': 330},
    {'date': '2000-12-01', 'series': 'Manufacturing', 'count': 240},
    {'date': '2001-01-01', 'series': 'Finance', 'count': 200},
    {'date': '2001-02-01', 'series': 'Finance', 'count': 210},
    {'date': '2001-03-01', 'series': 'Finance', 'count': 220},
    {'date': '2001-01-01', 'series': 'Services', 'count': 400},
    {'date': '2001-02-01', 'series': 'Services', 'count': 410},
    {'date': '2001-03-01', 'series': 'Services', 'count': 420},
]

source = pd.DataFrame(data_list)
source['date'] = pd.to_datetime(source['date'])

selection = alt.selection_point(fields=['series'], bind='legend')

chart = alt.Chart(source).mark_area().encode(
    alt.X('yearmonth(date):T'),
    alt.Y('sum(count):Q').stack('center'),
    alt.Color('series:N'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_params(
    selection
)

chart.show()