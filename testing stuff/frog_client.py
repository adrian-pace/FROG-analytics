import requests
from pprint import pprint
from flask import Flask, jsonify
from flask import request as flask_request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receiving_requests():
    if flask_request.method == 'POST':
        print(flask_request.get_json())
