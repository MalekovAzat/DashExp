# The file contains internal elements for cards and components 
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_devices.dependencies import Input, Output, State, MATCH, ALL
import dash_table
import plotly.express as px
import pandas
import io
import base64

def button(id, *, text='Empty'):
    return dbc.Button(
            text,
            color='link',
            id=id,
            className='text-body bg-success',
            style={
                'display': 'block',
                'margin': '10px auto',
                'font-size': '1.2em'
            }
        )

def upload(id='', *, multiple=False):
    return dcc.Upload(
            id=id,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files',
                       className='text-primary')
            ]),
            style={
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=multiple
        )

def labelWithInput(id, *, labelText):
    return html.Label(
            children=[
                labelText,
                dcc.Input(
                    id=id,
                    type='number',
                    placeholder='>=1',
                    min=1,
                    style={
                        'margin-left': '20px',
                        'width': '60px',
                    }
                ),
            ],
            style={
                'display': 'block',
                'margin-left': '10px'
            }
        )

def card(id:str, *, header:str, childs:list, app=None):
    @app.callback(
        Output(f'collapse-{id}', 'is_open'),
        [Input(f'toggle-{id}', 'n_clicks')],
        [State(f'collapse-{id}', 'is_open')]
    )
    def toggleButtonCallback(n_click, is_open):
        return not is_open if n_click else is_open

    return dbc.Card(
        id=id,
        children=[
            dbc.CardHeader(
                html.H6(
                    dbc.Button(
                        header,
                        color="link",
                        id=f'toggle-{id}',
                        className='text-body'
                    )
                )
            ),
            dbc.Collapse(
                id=f'collapse-{id}',
                children=childs,
                style={
                    'padding': '15px',
                }
            ),
        ],
        className='shadow',
        style={
            'margin': '10px 0',
        }
    )

def form(action, location):
    
    return html.Form(
        action=location,
        method="get",
        target='_blank',
        children=[
            html.Img(
                src=location,
                className='img-thumbnail',
                style={
                    'box-sizing': 'border-box',
                }
            ),
            html.Button(
                className="btn btn-success",
                type="submit",
                children=[
                    "Download"
                ],
                style={
                    'margin': '10px auto',
                    'display': 'block'
                }
            )
        ]
    )

def graph(points):

    return dcc.Graph(
        figure=px.line(points, x='x', y='y')
    )

def table(tableData):
    content_type, content_string = tableData.split(',')
    decoded = base64.b64decode(content_string)

    df = pandas.read_excel(io.BytesIO(decoded))

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records')
    )

def video(path):
    return html.Video(
        src=path,
        controls=True,
        style={
            'width': '100%'
        }
    )