import sys
import apsw
import hashlib
import app
import bcrypt

DATABASE_NAME = './tiny.db'



def init_db():
    """
    Initialises the database if it doesen't exist and adds fields.

    :return:
    """
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id integer PRIMARY KEY AUTOINCREMENT ,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL);''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            message_id integer PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            created_time NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message_content TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(user_id));''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
            announcement_id integer PRIMARY KEY AUTOINCREMENT, 
            author TEXT NOT NULL,
            text TEXT NOT NULL);''')

    except apsw.Error as e:
        print(e)
        sys.exit(1)


def add_user_to_db(user_to_add, password_to_add):
    """
    Adds a specified user to the database

    :param user_to_add:
    :param password_to_add:
    :return:
    """
    succesfull = False
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (user_name, password)'
                       'VALUES (?, ?)', (user_to_add, password_to_add))
        succesfull = True
    except apsw.Error as e:
        print(e)
        sys.exit(1)
    return succesfull

def get_user_data_from_db(user):
    try:
        conn = apsw.Connection(DATABASE_NAME)
        c = conn.cursor()
        c.execute('''
        SELECT *
        FROM users
        WHERE (user_name)''')

    except apsw.Error as e:
        print(e)
        sys.exit(1)

def get_all_messages_of_current_user():
    temp = a


def validate_login(username, password):
    """

    :param username: The user that is to be checked for in the database.
    :param password: The password that is to be checked.
    :return: Returns a bool if the login was valid or not.
    """
    result = False
    try:
        query = 'SELECT * FROM users WHERE user_name = (?)'
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute(query, (username,))
        fetch_result = cursor.fetchone()
        if not fetch_result:
            return result
        password_in_db = fetch_result[2]
        result = True if password_in_db == password else False
        # result = check_password(password, password_in_db)
        print(f'{password_in_db = }')
        print(f'{result = }')
    except apsw.Error as err:
        print(err)

    return result



def get_users_messages():
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
    except apsw.Error as err:
        print(err)
        app.logger.critical(f'There was a critical error when trying to access the database')
        sys.exit(1)

if __name__ == '__main__':
    a = 0
    add_user_to_db('test', 'test')