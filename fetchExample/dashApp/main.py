from asyncio import constants
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import redis
import requests

from io import BytesIO
import numpy as np

url = 'http://localhost:3000/get-graph-data'


app = dash.Dash(__name__)
r = redis.Redis()


def createLayout(application):
    application.layout = html.Div(children=[
        html.H1(
            id="header",
            children="FetchExample"),
        dcc.Graph(
            id="graph",
            style={
                'max-width': '700px',
            }
        ),
        html.Button('Perform Fetch Data', id='fetch-button'),
    ])


app.clientside_callback(
    """
def fetchData(startButtonClickCount):
    print('Fetch Data')

    data = requests.get(url=url)
    np_bytes = BytesIO(data.content)
    z = np.load(np_bytes, allow_pickle=True)
    print(z)
    return px.line({'time': z[0], 'cpuUsage': z[1]}, x='time', y='cpuUsage')
""",
    Output('graph', 'figure'),
    [Input('fetch-button', "n_clicks"), ])

if __name__ == "__main__":
    createLayout(app)
    app.run_server(debug=True)
