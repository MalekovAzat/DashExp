
# The class is a singletone
from dash_devices.dependencies import Input, Output, State, MATCH, ALL
from tools.storageProvider import storageProvider as sp
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import base64
import dash
import json
import datetime


def createTaskListTemplate(app, taskList=[], submitButtonCallback=None):
    return html.Div(
        id='task-container',
        children=[
            html.H3(children=[
                    'Task List'
                    ],
                    style={
                    'display': 'block',
                    'padding': '20px',
                    'font-weight': 'bolder',
                    'text-align': 'center',
                    }
                    ),
            html.Div(
                id='task-list',
                style={
                    'min-width': '450px',
                    'max-width': '500px',
                },
                children=createTasksCards(app, taskList, submitButtonCallback)
            )
        ]
    )


def createReportListTemplate(app):
    return html.Div(
        id='reports-wrapper',
        children=[
            html.H3(children=[
                    'Reports List'
                    ],
                    style={
                    'display': 'block',
                    'padding': '20px',
                    'font-weight': 'bolder',
                    'text-align': 'center',
                    }
                    ),
            html.Div(
                id='reports-container',
                children=[
                    createReportList(app, 'in-queue', 'In queue'),
                    createReportList(app, 'in-progress', 'In progress'),
                    createReportList(app, 'in-completed', 'Completed'),
                    createReportList(app, 'in-aborted', 'Aborted')
                ],
                style={
                    'min-width': '450px',
                    'max-width': '500px',
                }
            )
        ]
    )


def createTasksCards(app, taskList, submitButtonCallback):
    return [taskCard(app, info, submitButtonCallback) for info in taskList]


def taskCard(app, info, submitButtonCallback):
    @app.callback(
        Output(f'collapse-{info["name"]}', 'is_open'),
        [Input(f'toggle-{info["name"]}', 'n_clicks')],
        [State(f'collapse-{info["name"]}', 'is_open')]
    )
    def toggleButtonCallback(n_click, is_open):
        return not is_open if n_click else is_open

    app.callback(
        None,
        [
            Input(f'start-button-{info["name"]}', 'n_clicks'),
        ],
        [
            State(f'input-rep-{info["name"]}', 'value'),
            State(f'file-uploader-{info["name"]}', 'contents'),
            State(f'{info["name"]}', 'id')
        ]
    )(submitButtonCallback)
    # def func(n_clicks, reprValue, contents):
    #     print('!@#, Hello', n_clicks, reprValue, contents)

    collapseChildrenList = [
        dcc.Upload(
            id=f'file-uploader-{info["name"]}',
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
        ),

        html.Label(
            children=[
                "Number of repetitions:",
                dcc.Input(
                    id=f'input-rep-{info["name"]}',
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
                'margin-left': '10px'
            }
        ),

        dbc.Button(
            'Start task',
            color='link',
            id=f'start-button-{info["name"]}',
            className='text-body bg-success',
            style={
                'display': 'block',
                'margin': '10px auto',
                'font-size': '1.2em'
            }
        ),
    ]

    return dbc.Card(
        id=info['name'],
        children=[
            dbc.CardHeader(
                html.H6(
                    dbc.Button(
                        info['header'],
                        color="link",
                        id=f'toggle-{info["name"]}',
                        className='text-body'
                    )
                )
            ),
            dbc.Collapse(
                id=f'collapse-{info["name"]}',
                children=collapseChildrenList,
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

def createReportList(app, /, listId='empty-id', listName='empty name'):
    @app.callback(
        [
            Output(f'{listId}-p', 'children'),
            Output(f'{listId}-wrapper', 'style')
        ],
        [Input(f'{listId}-list', 'children')]
    )
    def func(childList):
        return f'Task count: {len(childList)}', {'display': 'none'} if len(childList) == 0 else {'display': 'block'}

    return html.Div(
        id=f'{listId}-wrapper',
        children=[
            html.Div(
                children=[
                    html.H6(
                        listName,
                        style={
                            'margin': '10px 0'
                        },
                        className='text-primary'
                    ),
                    html.P(id=f'{listId}-p', className='text-secondary')
                ]
            ),
            html.Div(
                id=f'{listId}-list',
                # children=createList(listId),
                children=[],
            )
        ],
        style={
            'display': 'none'
        }
    )

    # TODO: через этот компонент будет вызываться главный callback который рисует UI!


def createBindingComponent(app, componentId, callback):
    app.callback(
        None,
        [
            Input(f'{componentId}', 'children')
        ]
    )(callback)

    return html.Div(
        id=f'{componentId}',
        style={
            'display': 'none'
        }
    )


def createBindingProgressComponent(app, componentId, callback):
    app.callback(
        None,
        [
            Input(componentId, 'children')
        ],
        [
            State('in-progress-list', 'children'),
        ]
    )(callback)

    return html.Div(
        id=componentId,
        style={
            'display': 'none'
        }
    )

def createRefreshComponent(app, componentId, callback):
    app.callback(
        [
            Output('in-queue-list', 'children'),
            Output('in-progress-list', 'children'),
            Output('in-completed-list', 'children'),
            Output('in-aborted-list', 'children'),
        ],
        [
            Input(componentId, 'children')
        ]
    )(callback)
    
    return html.Div(
        id=componentId,
        style={
            'display': 'none'
        }
    )

def createList(listName):
    if listName == 'in-queue':
        return createInQueueList()
    elif listName == 'in-progress':
        return createInProgressList()
    elif listName == 'in-completed':
        return createInCompletedList()
    elif listName == 'in-aborted':
        return createInAbortedList()
    else:
        print('Incorrect list name', listName)


def createInQueueList():
    return [createTaskInQueueReport(i) for i in sp().valuesFromList('in-queue')]


def createInProgressList():
    return [createTaskInProgressReport(i) for i in sp().valuesFromList('in-progress')]


def createInCompletedList():
    return [createTaskInCompletedReport(i) for i in sp().valuesFromList('in-completed')]


def createInAbortedList():
    return [createTaskInAbortedReport(i) for i in sp().valuesFromList('in-aborted')]

def createTaskInQueueReport(taskId):
    return html.Div(
        id=f'task-{taskId}',
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
            html.P(f'added: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
                   className="text-secondary",
                   style={'margin-left': '10px', 'font-size': '0.8em'}),
            dbc.Button(
                id={
                    'type': 'abort-button',
                    'index': taskId
                },
                children=[
                    'Abort'
                ],
                style={
                    'margin': '10px auto',
                    'display': 'block'
                }
            )
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin': '10px 0',
            'border-radius': '5px',
        }
    )


def createTaskInProgressReport(taskId):
    return html.Div(
        id=f'task-{taskId}',
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
            html.Div(
                children=[
                    dbc.Progress(id=f'progress-{taskId}'),
                ],
                style={
                    'margin': '5px 20px'
                }
            ),
            dbc.Button(
                id={
                    'type': 'abort-button',
                    'index': taskId
                },
                children=[
                    'Abort'
                ],
                style={
                    'margin': '10px auto',
                    'display': 'block'
                }
            )
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin': '10px 0',
            'border-radius': '5px',
        }
    )


def createTaskInCompletedReport(taskId):
    location = f'download/result-{taskId}.jpg'

    return html.Div(
        id=f"task-{taskId}",
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
            # html.A('Link to donload', className='stretched-link',href=location, style={'margin': '5px 20px'}),
            html.Form(
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
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin': '10px 0',
            'border-radius': '5px',
        }
    )


def createTaskInAbortedReport(taskId):
    return html.Div(
        id=f"task-{taskId}",
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin': '10px 0',
            'border-radius': '5px',
        }
    )

def main():
    pass


if __name__ == '__main__':
    main()
