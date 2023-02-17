from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h3>drop-1 compute</h3>"
