from flask import Flask
from flask_restful import Api, Resource, reqparse
import psycopg
import os

DATABASE_URL = os.environ['DATABASE_URL']
conn_dict = psycopg.conninfo.conninfo_to_dict(DATABASE_URL)

with psycopg.connect(**conn_dict) as first_conn:
    with first_conn.cursor() as first_cur:
        try:
            first_cur.execute("""
                CREATE TABLE messages (
                    id integer,
                    content text)
                """)
            
            first_conn.commit()
        except:
            pass

app = Flask(__name__)
api = Api(app)

messages = [{"id": 1, "content": "hi"}, {"id": 2, "content": "Hello, world"}, {"id": 3}]

def get_standart_json_error(message: str, code: int):
    return {"errors": {str(code): {"message": message}}}

def message_sql_formatter(message):
    _id = message[0]
    _content = message[1]

    return {
        "id": _id,
        "content": _content
    }


class MessagesResource(Resource):
    def get(self, id=0):
        with psycopg.connect(**conn_dict) as conn:
            with conn.cursor() as cur:
                if id == 0:
                    cur.execute("SELECT * FROM messages")
                    sql_messages = cur.fetchall()
                    json_messages = []
                    
                    if sql_messages:
                        for i in sql_messages:
                            json_messages.append(message_sql_formatter(i))

                        return json_messages, 200
                    return get_standart_json_error("Messages not found", 404), 404
                else:
                    cur.execute("SELECT * FROM messages WHERE id = %s" % (id))
                    message = cur.fetchone()
                    
                    if message:
                        return message_sql_formatter(message), 200
        return "Message not found", 404
    def post(self, id=0):
        parser = reqparse.RequestParser()
        parser.add_argument("content")
        params = parser.parse_args()

        with psycopg.connect(**conn_dict) as conn:
            with conn.cursor() as cur:
                if id == 0:
                    try:
                        cur.execute(f"SELECT MAX(id) AS id FROM messages")
                        sql_column = cur.fetchone()
                        id = int(sql_column[0]) + 1
                    except TypeError:
                        id = 1

                cur.execute(f"INSERT INTO messages VALUES ({str(id)},'{params['content']}')")

                conn.commit()
        
        return {"id": id, "content": params["content"]}, 200
    
    def delete(self, id=0):
        with psycopg.connect(**conn_dict) as conn:
            with conn.cursor() as cur:
                if id == 0:
                    cur.execute("DELETE FROM messages")
                    conn.commit()
                    return {"message": "Succefully deleted all messages"}, 200
                else:
                    cur.execute(f"DELETE FROM messages WHERE id = {id}")
                    conn.commit()
                    return {"message": "Succefully deleted message"}, 200

api.add_resource(MessagesResource, "/messages", "/messages/", "/messages/<int:id>")

if __name__ == '__main__':
    app.run(debug=True)
