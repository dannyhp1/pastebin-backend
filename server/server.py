import json
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector

mysql_config = {
  'user': 'dannyhp',
  'password': 'password',
  'host': '127.0.0.1',
  'database': 'pastebin',
  'auth_plugin': 'mysql_native_password'
}

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

    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor(buffered=True)

    query = ('INSERT INTO posts VALUES(%s, %s, %s, %s, %s)')
    cursor.execute(query, (id, author, text, type, current_time))

    connection.commit()
    cursor.close()
    connection.close()

    print('Created a new post: ({}, {}, {}, {})'.format(id, text, type, current_time))
    return jsonify({
      'status': 'success',
      'id': id
    })
  except:
    return jsonify({
      'status': 'error'
    })

@app.route('/pastebin_load/<id>', methods = ['GET'])
def get_post(id):
  connection = mysql.connector.connect(**mysql_config)
  cursor = connection.cursor(buffered=True)

  query = ('SELECT author, text, type, date FROM posts WHERE id = %s')
  cursor.execute(query, (id,))
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
    'date': date.ctime()
  })

if __name__ == '__main__':
  app.run(debug=True)