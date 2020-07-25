import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import redis
import datetime
import psutil
import json

app = dash.Dash(__name__)
r = redis.Redis()

def createLayout(application):
    application.layout = html.Div(children=[
        html.H1(
            id="header",
            children="CPU USAGE"),
        dcc.Graph(
            id="graph",
            style={
                'max-width': '700px',
            }
        ),
        html.Button('Start', id='start-button'),
        html.Button('Stop', id='stop-button'),
        html.Label(children=[
            "Frequency:",
            dcc.Input(id="frequency-value", type="number",
                      placeholder=">0.01", min=0.01),
        ],
            htmlFor="input1",
            style={
            'margin-left': '20px'
        }),
        html.Div(id='check-is-calculating', style={'display': 'none'}),
        html.Div(id='is-calculating', style={'display': 'none'}),
        html.Div(id='calculated-data', style={'display': 'none'}),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True)
    ])
        
@app.callback(
    Output(component_id='is-calculating', component_property='children'),
    [Input(component_id='start-button', component_property="n_clicks"),
     Input(component_id='stop-button', component_property="n_clicks"),
     Input(component_id='frequency-value', component_property="value")]
)
def startCalculate(startButtonClickCount, stopButtonClickCount, frequencyValue):
    callbackContext = dash.callback_context
    if not callbackContext.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = callbackContext.triggered[0]['prop_id'].split('.')[0]
        if (button_id == 'start-button'):
            return 1
        elif (button_id == 'stop-button'):
            return 0
    return 0

@app.callback(
    Output(component_id="graph", component_property='figure'),
    [
        Input(component_id="interval-component", component_property='n_intervals'),
        Input(component_id="interval-component", component_property='interval')
    ]
)
def redrowGraph(n_intervals, frequencyValue):
    graphData = r.get("chartData")
    if graphData is None:
        graphData = {
        "time":  [0,],
        "cpuUsage": [psutil.cpu_percent(),],
        }
        r.set('chartData', json.dumps(graphData))
        fig = px.line(graphData, x="time", y="cpuUsage")
        return fig
    
    graphData = json.loads(graphData)
    frequencyValue = frequencyValue / 1000;
    graphData['time'].append(graphData['time'][-1] + frequencyValue)
    graphData['cpuUsage'].append(psutil.cpu_percent())
    r.set('chartData', json.dumps(graphData))
    fig = px.line(graphData, x="time", y="cpuUsage")
    return fig

@app.callback(
    [Output(component_id="interval-component" ,component_property="interval"),
    Output(component_id="interval-component" ,component_property="disabled")],
    [Input(component_id='is-calculating', component_property="children"),
    Input(component_id='frequency-value', component_property="value")]
)
def checkIsCalculating(isCalculating, frequencyValue):
    if not isinstance(frequencyValue, (int, float, str)):
        return [0,True];
    frequencyValue = float(frequencyValue);
    
    if not (bool(int(isCalculating)) or frequencyValue < 0.1):
        return [0,True];
    return [frequencyValue *  1000, False]

if __name__ == "__main__":
    createLayout(app)
    app.run_server(debug=True)
