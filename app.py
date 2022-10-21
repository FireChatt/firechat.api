from flask import Flask, request, jsonify
import psycopg
from erlpack import pack, unpack
import os

DATABASE_URL = os.environ['DATABASE_URL']
conn_dict = psycopg.conninfo.conninfo_to_dict(DATABASE_URL)

def _script(filename, cursor):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            cursor.execute(f.read())
    except:
        pass

with psycopg.connect(**conn_dict) as first_conn:
    with first_conn.cursor() as first_cur:
        _script('sql/table_channels.sql', first_cur)
            
        first_conn.commit()

app = Flask(__name__)

def get_standart_json_error(message: str, code: int):
    return {"errors": {str(code): {"message": message}}}

def get_id(table: str) -> int:
     with psycopg.connect(**conn_dict) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT MAX(id) AS id FROM %s' % table)
            sql_column = cur.fetchone()
            return int(sql_column[0]) + 1

@app.route("/channels", methods=['GET'])
def channels_get():
    result = {}
    
    with psycopg.connect(**conn_dict) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM channels')
            fetched = cur.fetchone()
            
            result = unpack(fetched[1])
    
    return jsonify(result)

@app.route("/channels", methods=['POST'])
def channels_post():
    data: dict = request.json

    id_of_channel = get_id('channels')
    data.setdefault('id', id_of_channel)
    
    with psycopg.connect(**conn_dict) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO channels VALUES (%d,'%s')" % (id_of_channel,pack(data)))

            conn.commit()
   
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
