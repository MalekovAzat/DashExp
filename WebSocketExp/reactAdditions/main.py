import dash_devices
from dash_devices.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from dash_html_components.Div import Div

app = dash_devices.Dash(__name__)
app.config.suppress_callback_exceptions = True


app.layout = html.Div([
    html.H2("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),
])


@app.call_callback(Output(component_id='my-output', component_property='children'), [Input('my-input', 'value')])
def function(value):
    return value


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5000)
