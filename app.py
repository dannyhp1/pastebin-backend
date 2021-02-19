from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/ping')
def ping():
    return jsonify({ 'status': 'healthy', 'service': 'pastebin' })

if __name__ == '__main__':
    app.run(port=5000)