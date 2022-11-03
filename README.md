Changes made 1.

Preliminary plan:
Split the "App.py" script into multiple different files that handles specific aspects. For example "auth" and/or "login",
Database etc.


1. Use the python "secrets" library to generate a cryptographically secure secret key for the app.
2. Added a new table for users - Done















For storing passwords in the database, i used the "bcrypt" library, which simplies the hashing and salting off passwords.
However, for the record, if i were to do it manually, it works like this:
1. Take in the plaintext password.
2. Generate a salt string.
3. Append the salt to the password
4. Hash the salted password
5. Append the salt again to the hashed password, so it can be used when checking passwords against it.



libraries to download
pip install bcrypt
pip install flask_login
pip install flask
pip install wtforms

# Currently working on: Login

# TODO 1. Add a way to register an user.
# TODO 2. Add a way to logout a user.
# TODO 3. Implement the instant mesaging system.
# TODO if i have the time, set up a setup.py script for packages.


Sources used:

https://flask.palletsprojects.com/en/2.2.x/tutorial/templates/#register-a-user