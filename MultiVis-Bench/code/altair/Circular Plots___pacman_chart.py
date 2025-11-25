import numpy as np
import altair as alt

chart_wider_mouth = alt.Chart().mark_arc().encode(
    theta=alt.ThetaDatum((5 / 8) * np.pi).scale(None),
    theta2=alt.Theta2Datum((17 / 8) * np.pi),
    radius=alt.RadiusDatum(100).scale(None),
)

chart_wider_mouth.show()