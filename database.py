import sys
import apsw
import utils
from flask import current_app


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
        print('Initialising the database.')
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('''  CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY AUTOINCREMENT ,
            user_name       TEXT UNIQUE NOT NULL,
            password        BLOB NOT NULL,
            time_created    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            blocked_users   );''')

        cursor.execute('''  CREATE TABLE IF NOT EXISTS messages (
            message_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id       INTEGER NOT NULL,
            recipient_id    INTEGER NOT NULL,
            time_created    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message_content TEXT NOT NULL,
            FOREIGN KEY (recipient_id) REFERENCES users(user_id),
            FOREIGN KEY (sender_id) REFERENCES users(user_id));''')

        cursor.execute('''  CREATE TABLE IF NOT EXISTS announcements (
            announcement_id integer PRIMARY KEY AUTOINCREMENT, 
            author          TEXT NOT NULL,
            created_time    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            content         TEXT NOT NULL);''')

    except apsw.Error as e:
        print(f'The server was unable to initialize the database.')
        print(e)
        sys.exit(1)


def validate_login(user_id: str, password: str) -> bool:
    """

    :param user_id: The user that is to be checked for in the database.
    :param password: The password that is to be checked.
    :return: Returns a bool if the login was valid or not.
    """
    result = False

    query_username = \
        ''' SELECT password
            FROM users
            WHERE user_name = (?)'''

    # query_id = \
    #     ''' SELECT password
    #         FROM users
    #         WHERE user_id = (?)'''
    #
    # if isinstance(user_id, str):
    #     query = query_username
    # elif isinstance(user_id, int):
    #     query = query_id

    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute(query_username, (user_id,))
        fetch_result = cursor.fetchone()
        if not fetch_result:
            return result

        password_in_db = fetch_result[0]
        result = utils.check_password(password, password_in_db)
    except apsw.Error as err:
        current_app.logger.warning('There was an error when trying to validate a login.')
        current_app.logger.warning(err)
    return result


def add_user_to_db(user_to_add: str, password_to_add: bytes):
    """
    Adds a specified user to the database

    :param user_to_add:
    :param password_to_add:
    :return:
    """
    successful = False
    current_app.logger.debug(f'Executing query to add user. Username: {user_to_add}')

    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = \
            '''INSERT INTO users (user_name, password)
               VALUES (?, ?);'''

        cursor.execute(query, (user_to_add, password_to_add))
        successful = True
    except apsw.Error as e:
        print(e)
    return successful


def get_user_data_by_name(username: str):
    found_user = None
    current_app.logger.debug(f'Executing query to get user data. Username: {username}')
    try:
        query = '''
            SELECT *
            FROM users
            WHERE (user_name) = (?)'''
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        result = cursor.execute(query, (username, ))
        if not result:
            return found_user

        found_user = result.fetchone()
    except apsw.Error as err:
        current_app.logger.warning(f'Something went wrong when trying to get a users data.')
        current_app.logger.warning(err)
    return found_user


def get_user_data_by_id(user_id: int):
    found_user = None
    try:
        user_id = int(user_id)
    except ValueError:
        return None

    query = '''
    SELECT *
    FROM users
    WHERE (user_id) = (?)'''

    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        result = cursor.execute(query, (user_id, ))

        if not result:
            return found_user

        found_user = result.fetchone()
    except apsw.Error as err:
        current_app.logger.warning(f'Something went wrong when trying to get a users data.')
        current_app.logger.warning(err)
    return found_user



def post_announcement(user_name, message_content):
    successful = False
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = '''INSERT INTO announcements (author, content) VALUES (?, ?)'''
        cursor.execute(query, (user_name, message_content))
        successful = True
    except apsw.Error as err:
        current_app.logger.warning(f'The was an error when inserting an announcement')
        current_app.logger.warning(err)

    return successful

def get_users_messages(user_name):
    """
    Gets all of a user's messages.

    :param user_name:
    :return:
    """
    result = None
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = ''' SELECT *
                    FROM messages
                    INNER JOIN users u on u.user_id = messages.sender_id
                    WHERE user_name = (?)'''

        result = cursor.execute(query, (user_name,))

        if not result:
            return None

        result = result.fetchall()

    except apsw.Error as err:
        print(err)
    return result




def get_message_by_id(message_id):
    message = None
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = ''' SELECT *
                    FROM messages
                    WHERE message_id = (?)
                '''
        result = cursor.execute(query, (message_id,))
        if result:
            message = result.fetchone()
    except apsw.Error as err:
        print(err)
    return message


def send_message(sender, message):
    successful = False
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        query = '''INSERT INTO messages (sender_id, message_content) 
                   VALUES (?, ?);'''
        cursor.execute(query, (sender, message))
        successful = True
    except apsw.Error as err:
        print(err)

    return successful



if __name__ == '__main__':
    init_db()