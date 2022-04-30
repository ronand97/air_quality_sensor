from re import M
from turtle import title
import plotly.graph_objects as go

def create_plotly_line_chart(df):

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['pm2_5'],
            name="PM2.5"
            )
        )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df.index,
    #         y=[10.0] * len(df),
    #         name="Mean safe limit of PM2.5 exposure per year (WHO)",
    #         line=dict(dash="dot"),
    #         mode="lines"
    #     )
    # )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['pm10'],
            name="PM10"
        )
    )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df.index,
    #         y=[20.0] * len(df),
    #         name="Mean safe limit of PM10 exposure per year (WHO)",
    #         line=dict(dash="dot"),
    #         mode="lines"
    #     )
    # )

    fig.add_hline(y=10.0, line_width=3, line_dash="dash", line_color="darkblue", name="Mean safe limit of PM2.5 exposure (WHO)")
    fig.add_hline(y=20.0, line_width=3, line_dash="dash", line_color="darkred", name="Mean safe limit of PM10 exposure (WHO)")
    fig.update_layout(
        title="Measurements of PM2.5 and PM10 using SDS011 Sensor"
    )

    
    return fig