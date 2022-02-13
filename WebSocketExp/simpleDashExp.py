import dash_devices
from dash_devices.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from dash_html_components.Div import Div

import asyncio
import websockets
import threading
import time

app = dash_devices.Dash(__name__)

app.layout = html.Div([
    html.H2("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),
])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    [Input(component_id='my-input', component_property='value')]
)
async def update_output_div(input_value):
    return 'Output: {}'.format(input_value)

z = 10


def updateValue():
    global z
    z = z + 1
    print('hello')
    app.push_mods({'my-input': {
        'value': z
    }})
    threading.Timer(10, updateValue).start()


if __name__ == '__main__':
    threading.Timer(10, updateValue).start()
    app.run_server(debug=True)
