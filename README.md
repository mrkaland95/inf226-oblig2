Preliminary plan:
Split the "App.py" script into multiple different files that handles specific aspects. For example "auth" and/or "login",
Database etc.

Part 2A:
Notes about security.
1.Prepared statements have been implemented for all queries that are sent to the database.
2. Passwords are salted and hashed before being stored in the database, ensuring that even if a leak were to happen,
    the user's credentials cannot be used at another website.

3. The user password can still get leaked during transit from the client, since the current implementation only uses HTTP, with no TLS
    So obviously during an actual deployment, the server would have TLS certificate implemented to ensure this cannot happen.
    Notes on this here: https://developer.mozilla.org/en-US/docs/Web/Security/Insecure_passwords



# TODO
5. Use the python "secrets" library to generate a cryptographically secure secret key for the app.
6. Added a new table for users - Done


For storing passwords in the database, I used the "bcrypt" library, which simplifies the hashing and salting off passwords.
However, for the record, if I were to do it manually, it works like this:
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

# The structure could have an impact on the security
# beacuse it's hard to keep an overview of everything when it's structured in a single file.
# Another issue with the structure, is that 


Sources used:
https://flask.palletsprojects.com/en/2.2.x/tutorial/templates/#register-a-user
https://flask.palletsprojects.com/en/2.2.x/blueprints/
https://flask.palletsprojects.com/en/2.1.x/api/#sessions