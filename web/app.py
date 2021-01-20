from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='dist')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('dist/js', path)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(port=5000)