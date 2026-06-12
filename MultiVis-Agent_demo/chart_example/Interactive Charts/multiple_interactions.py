import altair as alt
import pandas as pd
import numpy as np
import datetime

np.random.seed(42)

num_movies = 300

ratings = ['G', 'NC-17', 'PG', 'PG-13', 'R']
genres = [
    'Action', 'Adventure', 'Black Comedy', 'Comedy',
    'Concert/Performance', 'Documentary', 'Drama', 'Horror', 'Musical',
    'Romantic Comedy', 'Thriller/Suspense', 'Western'
]

data = pd.DataFrame({
    'Title': [f'Movie {i}' for i in range(1, num_movies + 1)],
    'Worldwide_Gross': 10**(np.random.uniform(4, 9, num_movies)),
    'IMDB_Rating': np.random.uniform(3, 9, num_movies).round(1),
    'Release_Date': pd.to_datetime(np.random.randint(datetime.datetime(1970, 1, 1).toordinal(), datetime.datetime(2019, 1, 1).toordinal(), num_movies).astype('datetime64[D]')),
    'MPAA_Rating': np.random.choice(ratings, num_movies),
    'Major_Genre': np.random.choice(genres, num_movies),
    'Production_Budget': 10**(np.random.uniform(3, 8, num_movies)),
})

movies = alt.Data(values=data.to_dict('records'))

base = alt.Chart(movies).mark_point().transform_calculate(
    Rounded_IMDB_Rating="floor(datum.IMDB_Rating)",
    Big_Budget_Film="datum.Production_Budget > 100000000 ? 'Yes' : 'No'",
    Release_Year="year(datum.Release_Date)",
).transform_filter(
    alt.datum.IMDB_Rating > 0
).transform_filter(
    alt.FieldOneOfPredicate(field='MPAA_Rating', oneOf=ratings)
).encode(
    x=alt.X('Worldwide_Gross:Q').scale(domain=(100000, 10**9), clamp=True),
    y='IMDB_Rating:Q',
    tooltip="Title:N"
)

year_slider = alt.binding_range(min=1969, max=2018, step=1)
slider_selection = alt.selection_point(bind=year_slider, fields=['Release_Year'])

filter_year = base.add_params(slider_selection).transform_filter(slider_selection)

genre_dropdown = alt.binding_select(options=genres)
genre_select = alt.selection_point(fields=['Major_Genre'], bind=genre_dropdown)

filter_genres = base.add_params(genre_select).transform_filter(genre_select)

rating_radio = alt.binding_radio(options=ratings)
rating_select = alt.selection_point(fields=['MPAA_Rating'], bind=rating_radio)

rating_color = alt.when(rating_select).then(alt.Color("MPAA_Rating:N")).otherwise(alt.value("lightgray"))

highlight_ratings = base.add_params(rating_select).encode(color=rating_color)

input_checkbox = alt.binding_checkbox()
checkbox_selection = alt.param(bind=input_checkbox)

size_checkbox = alt.when(checkbox_selection).then(alt.Size('Big_Budget_Film:N')).otherwise(alt.value(25))

budget_sizing = base.add_params(checkbox_selection).encode(size=size_checkbox)

(filter_year | budget_sizing) & (highlight_ratings | filter_genres)