import json
import time
import uuid
from os import path
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import sqlite3

DATABASE_FILE = './server/database/pastebin.db'
PASTEBIN_CREATE_TABLE_QUERY = """
CREATE TABLE posts (
  id VARCHAR(128),
  author VARCHAR(128),
  text LONGTEXT NOT NULL,
  type VARCHAR(128) NOT NULL,
  date DATETIME NOT NULL,
  PRIMARY KEY (id)
);"""
PASTEBIN_INSERT_QUERY = """
INSERT INTO posts VALUES(?, ?, ?, ?, ?)"""
PASTEBIN_GET_QUERY = """
SELECT author, text, type, date FROM posts WHERE id = ?"""

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def main():
  return 'Welcome to the homepage.'

@app.route('/pastebin_save', methods = ['POST'])
def save_post():
  try:
    data = request.get_json()

    text = data['text']
    type = data['type']
    author = data['author']
    id = uuid.uuid4().hex
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    create_db(DATABASE_FILE, PASTEBIN_CREATE_TABLE_QUERY)
    insert_paste(DATABASE_FILE, PASTEBIN_INSERT_QUERY, (id, author, text, type, current_time))

    print('Created a new post: ({}, {}, {}, {})'.format(id, text, type, current_time))
    return jsonify({
      'status': 'success',
      'id': id
    })
  except RuntimeError as e:
    return jsonify({
      'status': 'error'
    })

@app.route('/pastebin_load/<id>', methods = ['GET'])
def get_post(id):
  connection = sqlite3.connect(DATABASE_FILE)
  cursor = connection.cursor()

  cursor.execute(PASTEBIN_GET_QUERY, (id,))
  result = cursor.fetchall()
  
  if len(result) != 1:
    cursor.close()
    connection.close()

    return jsonify({
      'status': 'error',
      'message': 'No post can be found associated with the given id.'
    })
  
  author, text, type, date,  = result[0]
  cursor.close()
  connection.close()

  return jsonify({
    'status': 'success',
    'author': str(author),
    'text': text,
    'type': type,
    'date': date
  })

def insert_paste(db_path, query, paste):
  connection = sqlite3.connect(db_path)
  cursor = connection.cursor()
  cursor.execute(query, paste)
  connection.commit()
  cursor.close()
  connection.close()

def create_db(db_path, query):
  # Check if the database exists; if it doesn't, create it.
  if not path.exists(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
  app.run(debug=True)
