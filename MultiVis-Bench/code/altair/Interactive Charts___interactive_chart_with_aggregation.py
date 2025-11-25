import altair as alt
import pandas as pd

data = {
    'IMDB_Rating': [7.5, 8.2, 6.8, 9.1, 5.5, 7.9, 8.5, 6.2, 7.1, 8.8,
                   4.8, 7.3, 8.0, 6.5, 9.3, 5.9, 7.7, 8.3, 6.9, 7.0,
                   8.1, 5.2, 6.7, 9.0, 7.6, 8.4, 6.0, 7.2, 8.9, 5.7,
                   7.4, 8.6, 6.3, 7.8, 8.7, 5.0, 6.6, 9.2, 7.5, 8.1,
                   4.5, 6.1, 8.8, 5.4, 7.0, 9.5, 6.4, 7.9, 5.8, 8.2,
                    8.0, 7.1, 6.2, 9.3, 5.1, 8.4, 7.7, 6.8, 8.9, 7.5],
    'Rotten_Tomatoes_Rating': [80, 92, 71, 95, 58, 85, 90, 65, 78, 93,
                               45, 75, 88, 69, 97, 61, 82, 89, 73, 76,
                               86, 49, 70, 94, 81, 88, 64, 74, 91, 60,
                               79, 90, 67, 83, 92, 55, 72, 96, 80, 85,
                               40, 63, 91, 52, 74, 98, 68, 84, 62, 87,
                               85, 77, 68, 95, 50, 89, 83, 70, 92, 81]
}
movies_df = pd.DataFrame(data)

slider = alt.binding_range(min=0, max=10, step=0.1)
threshold = alt.param(name="threshold", value=5, bind=slider)

alt.layer(
    alt.Chart(movies_df).mark_circle().encode(
        x=alt.X("IMDB_Rating:Q"),
        y=alt.Y("Rotten_Tomatoes_Rating:Q")
    ).transform_filter(
        alt.datum["IMDB_Rating"] >= threshold
    ),

    alt.Chart(movies_df).mark_circle().encode(
        x=alt.X("IMDB_Rating:Q").bin(maxbins=10),
        y=alt.Y("Rotten_Tomatoes_Rating:Q").bin(maxbins=10),
        size=alt.Size("count():Q")
    ).transform_filter(
        alt.datum["IMDB_Rating"] < threshold
    ),

    alt.Chart().mark_rule().encode(
        x=alt.X(datum=alt.expr(threshold.name), type="quantitative")
    )
).add_params(threshold)