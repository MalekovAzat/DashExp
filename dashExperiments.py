import dash
import dash_html_components as html

app = dash.Dash(__name__)
app.layout = html.Label(children=[
            "Frequency:"])
if __name__ == '__main__':
    app.run_server(debug=True)