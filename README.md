### Part 2A:

From the onset, it was obvious 



### Part 2B
I decided to use the flask blueprints the various utilties of the server into separate files

1. Things like the database code in it's own file, the frontend forms.
Authentication related code in the "auth" file.
Other routes in the "routes file."
Then lastly, various smaller utility functions in the "utils" file.

2. I also implemented hashing and salting for passwords when they are inserted into the database.

3. Implemented prepared statements for all queries to the database.


Notes about security.
1.Prepared statements have been implemented for all queries that are sent to the database.
2. Passwords are salted and hashed before being stored in the database, ensuring that even if a leak were to happen,
    the user's credentials cannot be used at another website.

3. The user password can still get leaked during transit from the client, since the current implementation only uses HTTP, with no TLS
    So obviously during an actual deployment, the server would have TLS certificate implemented to ensure this cannot happen.
    Notes on this here: https://developer.mozilla.org/en-US/docs/Web/Security/Insecure_passwords


### Running the server




libraries to download
pip install bcrypt
pip install flask_login
pip install flask
pip install wtforms

Currently working on: Login

1. [ ] TODO 1. Add a way to register an user.
2. [ ] TODO 2. Add a way to logout a user.
3. [ ] TODO 3. Implement the instant mesaging system.
4. [ ] TODO 4. if i have the time, set up a setup.py script for packages.

[//]: # (# The structure could have an impact on the security)

[//]: # (# beacuse it's hard to keep an overview of everything when it's structured in a single file.)

[//]: # (# Another issue with the structure, is that )


Various sources and resources used:

##### Blueprints

https://flask.palletsprojects.com/en/2.2.x/tutorial/templates/#register-a-user

https://flask.palletsprojects.com/en/2.2.x/blueprints/

Corey Schaffer Flask Project - Blueprints - https://youtu.be/Wfx4YBzg16s 

##### Logins

https://flask-login.readthedocs.io/en/latest/


##### Cookies and Sessions

https://brightsec.com/blog/csrf-token/

https://flask.palletsprojects.com/en/2.1.x/api/#sessions

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

##### Same Origin Policy:

https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy