from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import time
import uuid

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_FILE_NAME = '%s/pastebin.db' % CURRENT_DIRECTORY

CREATE_PASTEBIN_TABLE_QUERY = '''
CREATE TABLE pastebin (
  id VARCHAR(128) NOT NULL,
  author VARCHAR(128) NOT NULL,
  text LONGTEXT NOT NULL,
  language VARCHAR(128) NOT NULL,
  type VARCHAR(128) NOT NULL,
  date DATETIME NOT NULL,
  PRIMARY KEY (id)
);
'''

app = Flask(__name__)
CORS(app)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/ping')
def ping():
    return jsonify({ 'status': 'healthy', 'service': 'pastebin' })

@app.route('/v1/pastebin/save', methods = ['POST'])
def save_paste():
    initialize_tables()

    try:
        data = request.get_json()

        id = str(uuid.uuid4())
        author = data['author']
        text = data['text']
        language = data['language']
        type = data['type']
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        connection = sqlite3.connect(DATABASE_FILE_NAME)
        cursor = connection.cursor()

        cursor.execute('INSERT INTO pastebin VALUES(?, ?, ?, ?, ?, ?)', (id, author, text, language, type, current_time))

        connection.commit()
        cursor.close()
        connection.close()

        print('Created a new post: ({}, {}, {}, {}, {})'.format(id, text, language, type, current_time))
        
        return jsonify({
            'status': 'success',
            'id': id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Cannot save the new paste.',
            'error_message': str(e)
        })

@app.route('/v1/pastebin/<id>', methods = ['GET'])
def get_paste(id):
    initialize_tables()

    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    query = ('SELECT author, text, language, type, date FROM pastebin WHERE id = ?')
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    
    if len(result) != 1:
        cursor.close()
        connection.close()

        return jsonify({
        'status': 'error',
        'message': 'No post can be found associated with the given id.'
        })
    
    author, text, language, type, date = result[0]
    cursor.close()
    connection.close()

    return jsonify({
        'author': str(author),
        'text': text,
        'language': language,
        'type': type,
        'date': date
    })

@app.route('/v1/pastebin/all', methods = ['GET'])
def get_all_pastes():
    initialize_tables()

    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    query = ('SELECT id, author, text, language, type, date FROM pastebin')
    cursor.execute(query)
    results = cursor.fetchall()

    all_pastes = []
    for paste in results:
        id, author, text, language, type, date = paste
        all_pastes.append({
            'id': str(id),
            'author': str(author),
            'text': text,
            'language': language,
            'type': type,
            'date': date
        })
    
    return jsonify({
        'results': all_pastes,
    })

def create_table():
    print('Creating a table!')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    cursor.execute(CREATE_PASTEBIN_TABLE_QUERY)
    
    connection.commit()
    connection.close()

def insert_sample_data():
    print('Inserting sample data!')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(('INSERT INTO pastebin VALUES(?, ?, ?, ?, ?, ?)'), ('4084cd36-905d-4a94-902d-1c499f345931', 'phamdann', 'print(5)', 'python', 'pastebin', current_time))
    cursor.execute(('INSERT INTO pastebin VALUES(?, ?, ?, ?, ?, ?)'), ('b6733a91-09c3-4ebc-80bc-79e03fd3b360', 'phamdann', 'print("Hello world!")', 'python', 'coderpad', current_time))

    connection.commit()
    connection.close()

def initialize_tables():
    if os.path.exists(DATABASE_FILE_NAME):
        return
    
    print('There is currently no database. Creating it now...')
    create_table()
    insert_sample_data()

if __name__ == '__main__':
    app.run(port=5000)