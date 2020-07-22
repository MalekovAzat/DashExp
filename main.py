import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import threading as th

#  my imports
import repeatingTimer

app = dash.Dash(__name__)


def createLayout(application):
    application.layout = html.Div(children=[
        html.H1(
            id="header",
            children="CPU USAGE"),
        dcc.Graph(
            id="graph",
            figure=createGraph(),
            style={
                'max-width': '700px',
            }
        ),
        html.Button('Start', id='start-button'),
        html.Button('Stop', id='stop-button'),
        html.Label(children=[
            "Frequency:",
            dcc.Input(id="frequency-value", type="number",
                      placeholder=">0.01", min=0.01, value=1),
        ],
            htmlFor="input1",
            style={
            'margin-left': '20px'
        }),
        html.Div(id='intermediate-value', style={'display': 'none'}),
    ])

def createGraph():
    data = {
        "time":  np.arange(10),
        "cpuUsage": np.arange(10),
    }
    fig = px.line(data, x="time", y="cpuUsage")
    return fig

def timerCallback():
    print('HELLO')

@app.callback(
    Output(component_id='intermediate-value', component_property='children'),
    [Input(component_id='start-button', component_property="n_clicks"),
     Input(component_id='frequency-value', component_property="value")]
)
def startTimer(clickCount, frequencyValue):
    timer =  repeatingTimer.repeatingTimer(frequencyValue, redrowChart)
    timer.start()
    return ""

def redrowChart():
    print('Hello');


if __name__ == "__main__":
    createLayout(app)
    app.run_server(debug=True)
