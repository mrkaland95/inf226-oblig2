import sys
import apsw
import hashlib
import app
import bcrypt


def init_database():
    try:
        conn = apsw.Connection(main.DATABASE_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id integer PRIMARY KEY, 
            sender TEXT NOT NULL,
            message TEXT NOT NULL);''')

        c.execute('''CREATE TABLE IF NOT EXISTS announcements (
            id integer PRIMARY KEY, 
            author TEXT NOT NULL,
            text TEXT NOT NULL);''')

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id integer PRIMARY KEY,
            user_name TEXT NOT NULL,
            password TEXT NOT NULL);''')
    except apsw.Error as e:
        print(e)
        sys.exit(1)


def add_user_to_database(user_to_add, password_to_add):
    """
    Adds a specified user to the database

    :param user_to_add:
    :param password_to_add:
    :return:
    """
    try:
        conn = apsw.Connection(main.DATABASE_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_to_add, password_to_add))

    except apsw.Error as e:
        print(e)
        sys.exit(1)

def get_user_from_database(user):
    try:
        conn = apsw.Connection(main.DATABASE_NAME)
        c = conn.cursor()
        c.execute('''
        SELECT user
        FROM users
        WHERE (user_name)''')

    except apsw.Error as e:
        print(e)
        sys.exit(1)




def get_users_messages():
    try:
        connection = apsw.Connection(main.DATABASE_NAME)
        cursor = connection.cursor()
    except apsw.Error as err:
        print(err)
        main.app.logger.critical(f'There was a critical error when trying to access the database')
        sys.exit(1)

if __name__ == '__main__':
    a = 0
    add_user_to_database('test', 'test')