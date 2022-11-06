### Part 2A:



### Part 2B
I decided to use the flask blueprints the various utilties of the server into separate files

1. Things like the database code in it's own file, the frontend forms.
Authentication related code in the "auth" file.
Other routes in the "routes file."
Then lastly, various smaller utility functions in the "utils" file.

2. I also implemented hashing and salting for passwords when they are inserted into the database.

3. Implemented prepared statements for all queries to the database.


##### Features - Implemented and planned

So far i have implemented login and the ability to register new accounts, which are stored in an SQLite database.

There's also the ability to logout, which will reroute to the login page.

Planned was also the ability to have an account page, with perhaps ability to change some preferences etc.

There is also some logging adding, but not as much as i'd like to have.

Lastly for the message system, which i originally intended to be a little bit like Discord.

But at the time of writing this ended up more like an email client or something.

Admittedly i'd have like to have implemented more/better, but simply did not have the time.

##### Notes about security.

1. Prepared statements have been implemented for all queries that are sent to the database, and atleast while testing
    with SQLmap i did not find any sql injections.

2. Passwords are salted and hashed before being stored in the database, ensuring that even if a leak were to happen,
    the user's credentials cannot be used at another website.

3. The plaintext user password can still get leaked during transit from the client, since the current implementation only uses HTTP, with no TLS
    So obviously during an actual deployment, the server would have TLS certificate implemented to ensure this cannot happen.
    Notes on this here: https://developer.mozilla.org/en-US/docs/Web/Security/Insecure_passwords

4. From my basic understanding of XSS and testing in the various forms i did not find

##### Threat model

Data in my application goes like this



### Setting up and running the server

The following libraries are used outside of the standard library. To install them, run the following commands.


`pip install flask`

`pip install flask_login`

`pip install flask_wtf`

`pip install wtforms`

`pip install apsw`

`pip install bcrypt`

`pip install pygments`

Then, once all the packages are installed, navigate to the oblig2 folder and run the "flask run". Now the server *should* be up and running.

NOTE: The program was worked on and ran with Windows 10/11.

Tested with Python 3.9, but it *should* work back to version 3.7 or so i believe.

Also, i have absolutely no clue whether it works for Linux/macOS, only tested with Windows.








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

