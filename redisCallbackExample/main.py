import dash_devices
import dash_html_components as html
import multiprocessing as mp
from dash_devices.dependencies import Input, Output
from redis import StrictRedis
import time

app = dash_devices.Dash(__name__)
storage = StrictRedis(host='localhost', port=6379)

pubsub = storage.pubsub()

def task(*args):
    print('task - started')
    storage['task-info'] = 'startTask'
    time.sleep(3)
    storage['task-info'] = 'firstStage'
    time.sleep(3)
    storage['task-info'] = 'secondStage'
    time.sleep(3)
    storage['task-info'] = 'Done'

    print('task - ended')
 
class Example:
    def __init__(self, app):
        self.app = app

        self.app.layout = html.Div([
            html.Div("Redis Example"),
            html.Button(
                id='start-task-button',
                children=['Start Task']
            ),
            html.Div(
                id='task-status'
            )
        ])

        @self.app.callback(None, [Input('start-task-button', 'n_clicks')])
        def func(*args):
            worker = mp.Process(target=task, args = ())            
            worker.start()

    def redisCallback(self, message):
        print('message', message)
        self.app.push_mods({
            'task-status': {
                'children': storage.get('task-info').decode('utf-8'),
            }
        })

if __name__ == '__main__':
    z = Example(app)
    pubsub.psubscribe(**{'__keyspace@0__:*': z.redisCallback})
    pubsub.run_in_thread(sleep_time=.01)
    app.run_server(debug=True, host='0.0.0.0', port=5000)