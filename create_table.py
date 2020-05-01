#
# did not work because of
#                         ImportError: cannot import name 'config' from 'config'
#
#

import psycopg2
from config import config

def create_table():

    commands = ( """CREATE TABLE books(
                id SERIAL PRIMARY KEY,
                isbn VARCHAR NOT NULL UNIQUE,
                title VARCHAR NOT NULL,
                author VARCHAR NOT NULL,
                year INTEGER NOT NULL
                )""")
    conn = None
    try:
        param = config()
        print (param)

        # conn = psycopg2.connect(**param)
        # print(conn)
        #
        # cur = cunn.cursor()
        #
        # for command in commands:
        #     cur.execute(command)
        # cur.close()
        # conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_table()
