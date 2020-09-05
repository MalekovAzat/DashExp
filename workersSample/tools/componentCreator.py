
#The class is a singletone 
from dash_devices.dependencies import Input, Output, State
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
                    'text-align':'center',
                }
            ),
            html.Div(
                id='task-list',
                style={
                    'min-width':'450px',
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
                    'text-align':'center',
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
                    'min-width':'450px',
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
                        'margin-left':'20px',
                        'width':'60px',
                    }
                ),
            ],
            style={
                'margin-left':'10px'
            }
        ),

        dbc.Button(
            'Start task',
            color='link',
            id=f'start-button-{info["name"]}',
            className='text-body bg-success',
            style = {
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
            'margin':'10px 0',
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
                children=[]
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
        ],
        [
            State('in-queue-list', 'children'),
            State('in-progress-list','children'),
            State('in-completed-list','children'),
            State('in-aborted-list', 'children'),
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
            State('in-progress-list','children'),
        ]
    )(callback)

    return html.Div(
        id=componentId,
        style={
            'display': 'none'
        }
    )

    # TODO: refactor these methods
def createContainerForTasks(app_obj,/, containter_id="", header="default header"):
    # change the cout of task
    def onChildrenCountChanged(children):
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

# TODO: Добавить в будущем кнопку отмены
def createTaskInQueueReport(taskId):
    return html.Div(
        id=f'task-{taskId}',
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
            html.P(f'added: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
             className="text-secondary", 
             style={'margin-left': '10px', 'font-size': '0.8em'}),
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin':'10px 0',
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
            )
        ],
        className='shadow bg-light',
        style={
            'padding': '5px',
            'margin':'10px 0',
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
            'margin':'10px 0',
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
            'margin':'10px 0',
            'border-radius': '5px',
        }
    )

# change to just div
# def createTaskReport(app_obj, /, binding_id='',header='template header', update_interval=1000):
#     collapseChildren = [
#         dcc.Interval(id=f'progress-interval-{binding_id}', n_intervals=0, interval=update_interval, disabled=True),
#         html.Div(
#             children=[
#                 dbc.Progress(
#                     id=f'progress-bar-{binding_id}'
#                 ),
#             ],
#             style={
#                 'margin': '5px 20px'
#             }
#         ),
#         dbc.Button(
#             'Cancel',
#             className='text-body bg-danger',
#             style = {
#                 'display': 'block',
#                 'margin': '10px auto',
#                 'font-size': '1.2em',
#             }
#         ),
#         html.Div(
#             id=f'status-{binding_id}',
#             style={
#                 'display': 'none'
#             }
#         )
#     ]

#     return dbc.Card(
#         children=[
#             dbc.CardHeader(
#                 children=[
#                     html.H2(
#                         dbc.Button(
#                             header,
#                             id=f'toggle-{binding_id}',
#                             color='link',
#                             className='text-body',
#                             style={
#                                 'display': 'block',
#                             }
#                         )
#                     ),
#                     html.P(f'started: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', className="text-secondary", style={'margin-left': '10px', 'font-size': '0.8em'}),
#                 ]
#             ),
#             dbc.Collapse(
#                 id=f'task-collapse-{binding_id}',
#                 children=collapseChildren
#             )   
#         ],
#         className='shadow',
#         style={
#             'margin': '10px 0'
#         }
#     )

# def generateCallbacksForTaskReports(app_obj, \, max_task_report=100):
def generateCallbacksForTaskReports(app_obj, /, max_task_report=100):
    
    # TODO:может сработать но надо додумать эту идею
    # def factory(bind_id):
    #     def closedFunc(callback):
    #         def wrapper(*args):
    #             return callback(*args)
    #         return wrapper
    #     return closedFunc

    # Set callback from different place and add real process change
    for binding_id in range(1, max_task_report + 1):
        @app_obj.callback(
            Output(f'task-collapse-{binding_id}', 'is_open'),
            [Input(f'toggle-{binding_id}','n_clicks')],
            [State(f'task-collapse-{binding_id}', 'is_open')]
        )
        def toggleButtonCallback(n_click, is_open):
            if n_click:
                return not is_open
            return is_open

        @app_obj.callback(
                [
                    Output(f'progress-bar-{binding_id}', 'value'),
                    Output(f'progress-bar-{binding_id}', 'children'),
                    Output(f'status-{binding_id}', 'children'),
                    Output(f'progress-interval-{binding_id}', 'disabled')
                ],
                [Input(f'progress-interval-{binding_id}', 'n_intervals')]
        )
        # @factory(binding_id)
        def updateTaskStatus(n):
            callbackContext = dash.callback_context
            triggeredItem = callbackContext.triggered[0]
            
            if not dash.callback_context.triggered:
                return [0, '', sp().statusByName('executing'), False]
            
            unicId= getTaskId(triggeredItem, 2)

            progress = sp().progress(unicId)

            status = sp().status(unicId)
            if status == sp().statusByName('executing'):
                disabled = False
            else:
                disabled = True
            return [progress, f'{progress}' if progress >= 5 else "", status, disabled]

        @app_obj.callback(
            Output(f'info-{binding_id}', 'children'),
            [
                Input(f'status-{binding_id}', 'children'),
            ]
        )
        # @factory(binding_id)
        def updateCompletedInfo(status):
            if status == sp().statusByName('executing'):
                return ''
            elif status == sp().statusByName('aboted'):
                return ''
            elif status == sp().statusByName('complited'):
                callbackContext = dash.callback_context
                triggeredItem = callbackContext.triggered[0]
                print('triggeredItem', triggeredItem)
                unicId= getTaskId(triggeredItem, 1)
                output = sp().output(unicId)
                sp().setOutput(unicId, '')
                return output

def createDoneReport(taskId, path):
    unicId = sp().getFreeeId()

    # path = sp().output(taskId)

    return html.Div(
        id=f'report-{unicId}',
        children = [
            html.P(
                children=[f'Report {unicId}'],
                className='text-body',
                style={
                    'display': 'block',
                    'margin': '5px auto'
                }
            ),
            html.Div(
                # добавить превью для изображения
                children=[
                    html.P(f'Finished: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 
                        className="text-secondary", style={'margin-left': '10px', 'font-size': '0.8em'}),
                    html.P(children=[
                        'Download link: ',
                        html.A('file', href=path),
                    ])
                ]
            )
        ],
        className='shadow',
        style={
            'margin': '10px 0',
            'padding': '20px'
            
        }
    )

def createInfoKeeper(count):
    return [
        html.Div(
            id=f'info-{i}',
            style = {
                'display': 'none'
            }
        ) 
        for i in range (1, count + 1)
    ]

def getTaskId(triggeredItem, index):
    if not triggeredItem:
        return None

    taskId = triggeredItem['prop_id'].split('-')[index].split('.')[0]
    return int(taskId)

def getComponentId(triggeredItem, index):
    if not triggeredItem:
        return None

    componentId = triggeredItem['prop_id'].split('-')[index]
    return componentId

def main():
    pass

if __name__=='__main__':
    main()