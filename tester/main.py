

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
  




  
app = Flask(__name__)
  
  
app.secret_key = 'secretkey'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'cindycui'
app.config['MYSQL_DB'] = 'urldatabase'
 
#initialize mySQL
mysql = MySQL(app)

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "userID" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'userID' in request.form and 'password' in request.form:
        # Create variables for easy access
        userID = request.form['userID']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        hashedpass = generate_password_hash(password, "sha256")

       #cursor.execute('SELECT * FROM users WHERE userID = %s AND password = %s', (userID, hashedpass)); 
        cursor.execute('SELECT * FROM users WHERE userID = %s', (userID,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in database
        if account:
            if check_password_hash(account['password'], password): #authenticate password on account 
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['userID'] = account['userID']
                # Redirect to home page
                #return 'Logged in successfully!'
                return redirect(url_for('home'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = hashedpass
           #msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('userID', None)
   # Redirect to login page 




   return redirect(url_for('login'))



# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():



    # Output message if something goes wrong...
    msg = ''
    # Check if "userID", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'userID' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        userID = request.form['userID']
        password = request.form['password']
        email = request.form['email']




        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE userID = %s', (userID,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', userID):
            msg = 'userID must contain only characters and numbers!'
        elif not userID or not password or not email:
            msg = 'Please fill out the form!'
        else:
            #create hashed password
            newpass=generate_password_hash(password, "sha256")

            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (userID, newpass, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythonlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM urls')
        data = cursor.fetchall()
        
      # if request.method == 'POST' and 'URL' in request.form and 'Comment' in request.form:

          #  URLid = request.form['URL'] 
           # Comment=request.form['Comment'] 

          #  userID = session['userID'] 
          #  cursor.execute("INSERT INTO urls VALUES (%s,%s,%s)", (URLid,userID,time, Comment, )) 
          #  mysql.connection.commit()
  


        return render_template('home.html', userID=session['userID'], data=data)
        # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


