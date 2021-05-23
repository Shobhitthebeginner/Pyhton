import flask
from flask import request
from flask import jsonify

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    try:
        return jsonify({"response" : 'hi this is python'})
    except:
        return jsonify({"response" : 'error'})

