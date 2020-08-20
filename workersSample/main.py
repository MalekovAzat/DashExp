# The application imitates workers queue
import dashApp  

def main():
    app = dash.Dash(__name__)

    app.run_server(debug=True)

if __name__ == '__main__':
    main()