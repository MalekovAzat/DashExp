import dash_devices

from dashApp import dashApp
import dash_bootstrap_components as dbc
from tools.storageProvider import storageProvider as sp

import os
import quart

if __name__ == '__main__':
    dash = dash_devices.Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP,])
    @dash.server.route('/download/<path:path>')
    async def server_static(path):
        root_dir = os.getcwd()
        return await quart.send_from_directory(
            os.path.join(root_dir, 'download'), path, as_attachment=True
        )

    dashApp(dash)
    dash.run_server(debug=True, host='0.0.0.0', port=5000)