
# The class is a singletone
from dash_devices.dependencies import Input, Output, State, MATCH, ALL
from tools.storageProvider import storageProvider as sp
import tools.internalComponentCreator as Icc

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

def createTasksCards(app:object, tasks:list, submitButtonCallback:object) -> list:
    elements = []

    # TODO: добавить сюда вызов метода
    for task in tasks:
        internalElements = createInternalElements(app, task['interface'], submitButtonCallback, task['id'])
        elements.append(
            Icc.card(task['id'], header=task['header'], childs=internalElements, app=app)
        )
    return elements

def createInternalElements(app:object, internalItemList:list, submitButtonCallback:object, wrapperId) -> list:
    elements = []
    statesList = []
    inputList = []

    for item in enumerate(internalItemList):
        name = item[1]['name']
        if name == 'upload':
            statesList.append({
                'id': item[1]['id'],
                'prop': item[1]['prop']
            })
            elements.append(Icc.upload(item[1]['id'], **item[1]['kargs']))
        elif name == 'labelWithInput':
            statesList.append({
                'id': item[1]['id'],
                'prop': item[1]['prop'],
            })
            elements.append(Icc.labelWithInput(item[1]['id'], **item[1]['kargs']))
        elif name == 'button':
            inputList.append({
                'id': item[1]['id'],
                'prop': item[1]['prop'] 
            })
            elements.append(Icc.button(item[1]['id'], **item[1]['kargs']))
    
    statesList.append({'id': wrapperId, 'prop':'id'})
    
    createCallbackForClick(app, inputList, [], statesList, submitButtonCallback)

    return elements

# возможно не нужна или не пригодится
def createCallbackForClick(app, inputsList, outputsList, statesList, func):
    outputsList = [Output(item['id'], item['prop']) for item in outputsList] if len(outputsList) else None
    inputsList = [Input(item['id'], item['prop']) for item in inputsList] if len(inputsList) else [None]
    statesList = [State(item['id'], item['prop']) for item in statesList] if len(statesList) else [None]

    app.callback(
        outputsList,
        inputsList,
        statesList
    )(func)

def taskCard(app, info, submitButtonCallback):
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

    collapseChildrenList = [
        Icc.upload(f'file-uploader-{info["name"]}', True),
        Icc.labelWithInput(f'input-rep-{info["name"]}', 'Number of repetitions:'),
        Icc.button(f'start-button-{info["name"]}', 'Start task')
    ]

    return Icc.card(info['name'], info['header'], collapseChildrenList, app=app)

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
    taskList = sp().valuesFromList('in-completed')
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
    infoList = sp().infoByTask(taskId)
    taskName = infoList[0]
    childList = []
    if taskName == 'gray-shades':
        location = infoList[1]
        childList.append(
            Icc.form(location, location)
        )
    elif taskName == 'calc-sin':
        points = json.loads(infoList[1])
        childList.append(
            Icc.graph(points)
        )
    elif taskName == 'read-table':
        tableData = infoList[1]
        childList.append(
            Icc.table(tableData)
        )
    elif taskName == 'video-by-image':
        pathToVideo = infoList[1]
        childList.append(
            Icc.video(pathToVideo)
        )
    else:
        print('Invalid task name', taskName)
        return

    return html.Div(
        id=f"task-{taskId}",
        children=[
            html.P(f'Task {taskId}', style={'padding': '10px'}),
            *childList
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
