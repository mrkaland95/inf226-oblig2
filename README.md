### Part 2A:



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


### Setting up and running the server

The server includes a server.py script, so all *should* be necessary to run it, 
is to run the following command(while being in the "oblig2" as your working directory in your shell.)

`python setup.py install`

NOTE: You may or may not need to have your shell

If that doesen't work, the required libraries to run the server outside of the standard library are as follows:

`pip install flask`

`pip install flask_login`

`pip install flask_wtf`

`pip install wtforms`

`pip install apsw`

`pip install bcrypt`


Then, once all the packages are installed, navigate to the oblig2 folder and run the "flask run". Now the server *should* be up and running.

NOTE: The program was worked on and ran with Windows 10/11.

I have absolutely no clue whether it works for Linux/macOS


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

##### CSS

[Navbar](https://www.w3schools.com/css/css_navbar_horizontal.asp)

[Top Nav Bar](https://www.w3schools.com/howto/howto_js_topnav.asp)

##### Flask specific security

https://flask.palletsprojects.com/en/2.2.x/security/

##### XSS:

Don't use Alert() for XSS - https://www.youtube.com/watch?v=KHwVjzWei1c

