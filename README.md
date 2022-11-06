### Part 2B

##### Threat Model

###### Who would attack the server?

Attackers often attack a web server for a few reasons.

1. For monetary gain, by for example stealing information from the server, and/or installing ransomware.

2. People that for whatever reason do not like the service and their provider, often doing DoS attacks for example.

3. For the fun/challenge of it.

###### What can an attack do?

This highly depends on the specific vulnerability/exploit used.

But an attacker could for example use my server to get information from the database, which could then be used in other, more important places.

Or more maliciously, if they got control of the server, they could send out malicious HTML to users for example.

###### Are there limits to what we can sensibly protect against?

Sure, attackers can often find creative avenues to find new exploits, but even disregarding that,

it's difficult to protect against very large scale DDoS attacks for example, even though they can be mitigated.


##### Features - Implemented and planned

So far i have implemented login and the ability to register new accounts, which are stored in an SQLite database.

There's also the ability to logout, which will reroute to the login page.

Planned was also the ability to have an account page, with perhaps ability to change some preferences etc.

There is also some logging adding, but not as much as i'd like to have.

Lastly for the message system, which i originally intended to be a little bit like Discord.

But at the time of writing this ended up more like an email client or something.

I.e have a form that would display all the messages sent to the currently logged in user, with the recipient, time stamp etc.

Huge caveat though, the main function of the server isn't really functioning, i.e the message board that is supposed to show all the messages etc.


Admittedly i'd have like to have implemented more/better, but simply did not have the time.


##### Access Control Model

The Access Control Model, in simple terms, the process of verifying that the entity that is trying to access a resource,

has the permissions to do so. This is often implemented through a username/password, but can also be done with thinks like API keys.

Then, once authorized, the server/system, will give back the requested resource.

Of course, in this model, you can have various levels of permissions, for example a regular user would not have the same permissions

as an admin/root user.

##### Main Attack Vectors

In no particular order:

Weak or compromised credentials, pretty much the most common way that unauthorized access to a system is gained.

This can for example happen beacuse of a poor password, or alternatively when credentials have been leaked from other databases,

which are then used somewhere else.

Lack of encryption, specifically lack of use of TLS/HTTPS

SQL injections

DDoS attacks

Malware/Ransomware

##### Steps taken towards attack vectors

1. Prepared statements have been implemented for all queries that are sent to the database, and atleast while testing
    with SQLmap i did not find any sql injections.

2. Passwords are salted and hashed before being stored in the database, ensuring that even if a leak were to happen,
    the user's credentials cannot be used at another website.

3. The plaintext user password can still get leaked during transit from the client, since the current implementation only uses HTTP, with no TLS
    So obviously during an actual deployment, the server would have TLS certificate implemented to ensure this cannot happen.
    Notes on this here: https://developer.mozilla.org/en-US/docs/Web/Security/Insecure_passwords

4. From my basic understanding of XSS and testing in the various form i didn't see any obvious opportunities to use it.

5. I *think* CSRF vulnerabilities should be handled for the various forms, with CSRF tokens added. 


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

