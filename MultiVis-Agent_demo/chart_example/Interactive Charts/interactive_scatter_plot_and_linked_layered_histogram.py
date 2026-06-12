import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)

male_height_mean = 70
male_height_std = 6
male_weight_mean = 200
male_weight_std = 130
male_age_mean = 43
male_age_std = 7

female_height_mean = 63
female_height_std = 5
female_weight_mean = 170
female_weight_std = 90
female_age_mean = 50
female_age_std = 5

num_samples = 1000

source = pd.DataFrame({
    'gender': ['M']*num_samples + ['F']*num_samples,
    'height':np.concatenate((
        np.random.normal(male_height_mean, male_height_std, num_samples),
        np.random.normal(female_height_mean, female_height_std, num_samples)
    )),
    'weight': np.concatenate((
        np.random.normal(male_weight_mean, male_weight_std, num_samples),
        np.random.normal(female_weight_mean, female_weight_std, num_samples)
    )),
    'age': np.concatenate((
        np.random.normal(male_age_mean, male_age_std, num_samples),
        np.random.normal(female_age_mean, female_age_std, num_samples)
        ))
    })

selector = alt.selection_point(fields=['gender'])

color = (
    alt.when(selector)
    .then(alt.Color("gender:N"))
    .otherwise(alt.value("lightgray"))
)

base = alt.Chart(source).add_params(selector)

points = base.mark_point().encode(
    alt.X('mean(height):Q'),
    alt.Y('mean(weight):Q'),
    color=color,
)

hists = base.mark_bar().encode(
    alt.X('age').bin(step=5),
    alt.Y('count()').stack(None),
    alt.Color('gender:N')
).transform_filter(
    selector
)

points | hists