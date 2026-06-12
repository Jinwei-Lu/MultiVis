import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
ages = np.arange(0, 91, 5)
data = []
for age in ages:
    people = np.random.normal(loc=1000000 - age * 5000, scale=200000, size=50)
    data.append(people)

df_list = []
for i, age in enumerate(ages):
    df_temp = pd.DataFrame({'age': [age] * len(data[i]), 'people': data[i]})
    df_list.append(df_temp)
df = pd.concat(df_list)

chart = alt.Chart(df).mark_boxplot(extent='min-max', outliers=False).encode(
    x='age:O',
    y='people:Q'
)

chart