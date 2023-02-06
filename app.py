from os import environ

HOST, USER, PASS = environ['HOST'], environ['USER'], environ['PASS']

from mysql.connector import connect, Error
from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from mysql.connector.cursor import CursorBase

def execute(sql: str, *params) -> 'CursorBase':
    sql = sql.format(*params)
    c = None

    try:
        with connect(
            host=HOST,
            user=USER,
            password=PASS,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                c = cursor
        return c
    except Error as e:
        print(e)

def select(sql: str, mode: Literal['a', 'o'], *params) -> Union[tuple, list[tuple], None]:
    c = execute(sql, *params)
    if mode is 'a':
        return c.fetchall()
    elif mode is 'o':
        return c.fetchone()

def execute_script(filename: str, *params):
    sql = ''
    with open(f'sql/{filename}.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    execute(sql, *params)

execute_script('tables/users')


from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=[ 'GET' ])
def root():
    return select('SELECT * FROM users', 'a')

if __name__ == '__main__':
    app.run(debug=True)
