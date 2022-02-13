import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State

import multiprocessing as mp
import time

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button('Button 1', id='btn-1'),
    html.Button('Button 2', id='btn-2'),
    html.Div('Div 1', id='div-1'),
    html.Div('Div 2', id='div-2'),
    html.Div(id='container')
])

@app.callback(Output('div-1','children'),
            [Input('btn-1', 'n_clicks')]
)
def call1(n):
    print(n)
    callbackContext = dash.callback_context
    print('call1',callbackContext.triggered)
    if not callbackContext.triggered:
        return ['']

    ctx = dash.callback_context
    time.sleep(3)

    print("!@######")
    return 'HELLO'

@app.callback(Output('div-2','children'),
            [Input('btn-2', 'n_clicks')]
)
def call2(n):
    callbackContext = dash.callback_context
    print(callbackContext.triggered)
    if not callbackContext.triggered:
        return ''
    print('start a process')
    return ''

@app.callback(Output('container', 'children'),
              [Input('div-2', 'children'),
              Input('div-1', 'children')])
def display(div1, div2):
    print(dash.callback_context.triggered)
    return div1

if __name__ == '__main__':
    app.run_server(debug=True)