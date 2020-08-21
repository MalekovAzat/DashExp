
#The class is a singletone 
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import base64
import dash
import json
import datetime

# The function create an accordion item, with additional options
def createAccordionItem(appObj, index, /, header='Template header', description='Template description', upload_component=False, counter_component=False):
    collapseChildren=[
        dbc.CardBody(description),
    ]

    if upload_component:
        collapseChildren.append(
            dcc.Upload(
                    id=f'file-uploader-{index}',
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
                    multiple=True
                )
        )

    if counter_component:
        collapseChildren.append(
            html.Label(children=[
                "Number of repetitions:",
                dcc.Input(
                    id=f'input-rep-{index}',
                    type='number',
                    placeholder='>=1',
                    min=1,
                    style={
                        'margin-left':'20px',
                        'width':'60px',
                    }
                ),
            ]),
        )

    def toggle_callback(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    appObj.callback(
        Output(f'collapse-{index}', 'is_open'),
        [Input(f'group-{index}-toggle', 'n_clicks')],
        [State(f'collapse-{index}', 'is_open')]
    )(toggle_callback)

    def start_button_callback(n_click, rep_count, input_data):
        if not dash.callback_context.triggered:
            return ''

        task_info = {
            'repeatCount': rep_count,
            'imageData': input_data,
            'taskName': 'default name'
        }
        return json.dumps(task_info)

    appObj.callback(
        Output(f'task-info-{index}', 'children'),
        [
            Input(f'start-button-{index}','n_clicks')
        ],
        [
            State(f'input-rep-{index}', 'value'),
            State(f'file-uploader-{index}', 'contents'),
        ]
    )(start_button_callback)

    collapseChildren.append(
        dbc.Button(
            'Start task',
            color="link",
            id=f"start-button-{index}",
            className='text-body bg-success',
            style = {
                'display': 'block',
                'margin': '10px auto',
                'font-size': '1.2em'
            }
        )
    )

    collapseChildren.append(
        html.Div(
            id=f'task-info-{index}',
            style={
                'display': 'none',
            }
        )
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        header,
                        color="link",
                        id=f"group-{index}-toggle",
                        className='text-body'
                    )
                )
            ),
            dbc.Collapse(
                id=f"collapse-{index}",
                children=collapseChildren,
                style={
                    'padding': '15px',
                }
            ),
        ],
        className='shadow',
        style={
            'margin':'10px 0',
        }
    )

def subscribeTaskHandler(app_obj, ids_prefixes, task_count, /, handler_id='server-information', task_callback=None):
    if not task_callback:
        def task_callback(*args):
            return dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    app_obj.callback(
        Output(handler_id, 'children'),
        [Input(f'{ids_prefixes}-{i}', 'children') for i in range(1, task_count + 1)],
        [State(handler_id, 'children')]
    )(task_callback)

# TODO: сделать потом это аккордионом
def createContainerForTasks(app_obj,/, containter_id="", header="default header"):
    # change the cout of task
    def onChildrenCountChanged(children):
        print(len(children))
        return f'Task count: {len(children)}', {'display': 'none'} if len(children) == 0 else {'display': 'block'}
    app_obj.callback(
        [
            Output(f'{containter_id}-p', 'children'),
            Output(f'{containter_id}', 'style')
        ],
        [Input(f'{containter_id}-container', 'children')]
    )(onChildrenCountChanged)

    return html.Div(id=containter_id,
        children = [
            html.Div(
                children=[
                    html.H2(header,
                        style={
                            'margin': '10px 0'
                        },
                        className='text-primary'
                    ),
                    html.P(id=f'{containter_id}-p', className='text-secondary')
                ]
            ),
            html.Div(
                id=f'{containter_id}-container',
                children=[
                ]
            )
        ],
        style={
            'display': 'none'
        }
    )

# change to just div
def createTaskReport(app_obj, /, buinding_id='',header='template header', update_interval=1000):
    collapseChildren = [
        dcc.Interval(id=f'progress-interval-{buinding_id}', n_intervals=0, interval=update_interval),
        dbc.Progress(id=f'progress-bar-{buinding_id}'),
        dbc.Button(
            'Cancel',
            className='text-body bg-danger',
            style = {
                'display': 'block',
                'margin': '10px auto',
                'font-size': '1.2em',
            }
        )
    ]

    return dbc.Card(
        children=[
            dbc.CardHeader(
                children=[
                    html.H2(
                        dbc.Button(
                            header,
                            id=f'toggle-{buinding_id}',
                            color='link',
                            className='text-body',
                            style={
                                'display': 'block',
                            }
                        )
                    ),
                    html.P(f'started: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', className="text-secondary", style={'margin-left': '10px', 'font-size': '0.8em'}),
                ]
            ),
            dbc.Collapse(
                id=f'task-collapse-{buinding_id}',
                children=collapseChildren
            )   
        ],
        className='shadow',
        style={
            'margin': '10px 0'
        }
    )

# def generateCallbacksForTaskReports(app_obj, \, max_task_report=100):
def generateCallbacksForTaskReports(app_obj, /, max_task_report=100):
    # toggleButtonCallback
    def toggleButtonCallback(n_click, is_open):
        if n_click:
            return not is_open
        return is_open
    
    # Set callback from different place and add real process change
    def updateProgressBarCallback(n):
        callbackContext = dash.callback_context
        progress = 47
        triggeredItem = callbackContext.triggered[0]
        
        return [progress, f'{progress}' if progress >= 5 else ""]

    for buinding_id in range(1, max_task_report+1):
        app_obj.callback(
            Output(f'task-collapse-{buinding_id}', 'is_open'),
            [Input(f'toggle-{buinding_id}','n_clicks')],
            [State(f'task-collapse-{buinding_id}', 'is_open')]
        )(toggleButtonCallback)

        app_obj.callback(
            [
                Output(f'progress-bar-{buinding_id}', 'value'),
                Output(f'progress-bar-{buinding_id}', 'children')
            ],
            [Input(f'progress-interval-{buinding_id}', 'n_intervals')]
        )(updateProgressBarCallback)

def main():
    s = СomponentCreator()
    print(s)
    s1 = СomponentCreator()
    print(s1)

if __name__=='__main__':
    main()