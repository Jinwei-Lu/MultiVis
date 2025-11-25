import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/debate.sqlite')

query = '''
SELECT T1.Venue, T1.Num_of_Audience, T2.If_Affirmative_Win
FROM debate AS T1
INNER JOIN debate_people AS T2
ON T1.Debate_ID = T2.Debate_ID;
'''

df = pd.read_sql_query(query, conn)

conn.close()

df['If_Affirmative_Win'] = df['If_Affirmative_Win'].map({'T': 'Yes', 'F': 'No'})

brush = alt.selection_interval()
win_condition = alt.condition(brush, "If_Affirmative_Win", alt.value('lightgray'))
base = alt.Chart(df).add_params(brush)

points = base.mark_point().encode(
    x=alt.X('Num_of_Audience:Q', title='Number of Audience'),
    y=alt.Y('Venue:N', title='Venue'),
    color=win_condition
)

tick_axis = alt.Axis(labels=False, domain=False, ticks=False)
tick_color = win_condition

x_ticks = base.mark_tick().encode(
    alt.X('Num_of_Audience:Q', axis=tick_axis),
    alt.Y('If_Affirmative_Win:N', title='', axis=tick_axis),
    color=tick_color
)

y_ticks = base.mark_tick().encode(
    alt.X('If_Affirmative_Win:N', title='', axis=tick_axis),
    alt.Y('Venue:N', axis=tick_axis),
    color=tick_color
)

y_ticks | (points & x_ticks)