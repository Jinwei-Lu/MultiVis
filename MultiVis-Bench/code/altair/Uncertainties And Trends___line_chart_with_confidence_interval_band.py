import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)

years = np.arange(1970, 1981)
data = []
for year in years:
    mpg_mean = 20 + (year - 1970) * 0.5
    mpg_std = 3
    mpg_values = np.random.normal(mpg_mean, mpg_std, 50)
    for mpg in mpg_values:
        data.append({'Year': year, 'Miles_per_Gallon': mpg})

source = pd.DataFrame(data)

line = alt.Chart(source).mark_line().encode(
    x='Year:O',
    y='mean(Miles_per_Gallon):Q'
)

band = alt.Chart(source).mark_errorband(extent='stdev').encode(
    x='Year:O',
    y='Miles_per_Gallon:Q'
)

chart = band + line

chart