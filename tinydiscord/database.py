import sys
import apsw
from .utils import check_password

DATABASE_NAME = './tiny.db'

"""
File for handling the database logic:
Initialization, requests from the database, insertions etc.
"""


def init_db():
    """
    Initialises the database if it doesen't exist and adds fields.

    :return:
    """
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('''  CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY AUTOINCREMENT ,
            user_name       TEXT UNIQUE NOT NULL,
            password        TEXT NOT NULL,
            blocked_users   );''')

        cursor.execute('''  CREATE TABLE IF NOT EXISTS messages (
            message_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id       INTEGER NOT NULL,
            created_time    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message_content TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(user_id));''')

        cursor.execute('''  CREATE TABLE IF NOT EXISTS announcements (
            announcement_id integer PRIMARY KEY AUTOINCREMENT, 
            author          TEXT NOT NULL,
            content         TEXT NOT NULL);''')

    except apsw.Error as e:
        print(f'The server was unable to initialize the database.')
        print(e)
        sys.exit(1)


def get_announcements():
    temp = 0


def validate_login(username: str, password: str) -> bool:
    """

    :param username: The user that is to be checked for in the database.
    :param password: The password that is to be checked.
    :return: Returns a bool if the login was valid or not.
    """
    result = False
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = ''' SELECT password
                    FROM users
                    WHERE user_name = (?);'''
        cursor.execute(query, (username,))
        fetch_result = cursor.fetchone()
        if not fetch_result:
            return result
        password_in_db = fetch_result[0]
        # result = True if password_in_db == password else False
        result = check_password(password, password_in_db)

    except apsw.Error as err:
        print(err)

    return result


def add_user_to_db(user_to_add: str, password_to_add: bytes):
    """
    Adds a specified user to the database

    :param user_to_add:
    :param password_to_add:
    :return:
    """
    successful = False
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = '''INSERT INTO users (user_name, password)
                   VALUES (?, ?);'''
        cursor.execute(query, (user_to_add, password_to_add))
        successful = True
    except apsw.Error as e:
        print(e)
    return successful


def get_user_data_from_db(user):
    found_user = None
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        found_user = cursor.execute('''
                    SELECT *
                    FROM users
                    WHERE (user_name) = (?);''', (user,))
    except apsw.Error as err:
        print(err)
    return found_user


def get_users_messages(user_name):
    """
    Gets all of a user's messages.
    :param user_name:
    :return:
    """
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = ''' SELECT *
                    FROM messages
                    WHERE sender_id = (?);
                '''
    except apsw.Error as err:
        print(err)


def get_specific_message(message_id):
    """
    Fetches a specific message with a specific id.
    """
    message = None
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = ''' SELECT *
                    FROM messages
                    WHERE message_id = (?)
                '''
        result = cursor.execute(query, (message_id, ))
        if result:
            message = result.fetchone()
    except apsw.Error as err:
        print(err)
    return message


if __name__ == '__main__':
    init_db()