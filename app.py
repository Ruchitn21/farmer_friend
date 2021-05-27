#Import necessary libraries

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
import numpy as np
import os

from tensorflow import keras
from PIL import Image, ImageOps
import numpy as np
 
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model

 
def pred_cot_dieas(cott_plant):    

    np.set_printoptions(suppress=True)
    
    model = keras.models.load_model('keras_model.h5')

    print('@@ Model loaded')

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    image = Image.open(cott_plant)

    size = (224, 224)
    
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    image_array = np.asarray(image)

    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    data[0] = normalized_image_array

    prediction_array = model.predict(data)

    pred= np.argmax(prediction_array)
 
    if pred == 0:
        return "Potato Early Blight", 'p_early_blight.html'

    elif pred == 1:
        return 'Potato Healthy', 'p_healthy.html' 

    elif pred == 2:
        return 'Potato Late Blight', 'p_late_blight.html' 

    elif pred == 3:
        return "Tomato Bacterial Spot", 't_bacterial_spot.html'

    elif pred == 4:
        return "Tomato Healthy", 't_healthy.html'

    elif pred == 5:
        return "Tomato Late Blight", 't_late_blight.html'

    elif pred == 6:
        return "Tomato Leaf Mold", 't_leaf_mold.html'

     
app = Flask(__name__)

# ===================================== LOGIN SIGNUP SYSTEM =============================================

app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ruchit21'
app.config['MYSQL_DB'] = 'farmfriend'

mysql = MySQL(app)
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
#     user= ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg,user=username)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        final_password= request.form['password-2']
        email = request.form['email']
        
        print(f"Username : {username}")
        print(f"Password : {password}")
        print(f"email : {email}")
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        elif password!=final_password:
            msg="Re-Entered Password should match with Original"
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html', msg = msg)
          
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

  

# =======================================================================================================
@app.route("/index", methods=['GET', 'POST'])
def home():
    
    if 'loggedin' in session:
        return render_template('index.html', user=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/account", methods=['GET', 'POST'])
def account():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('account.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/predict", methods = ['GET','POST'])
def predict():

     isAvail=""
     if request.method == 'POST':
        file = request.files['image'] # fet input
        filename = file.filename

        print("@@ Input posted = ", filename)
         
        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)
        
        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas(cott_plant=file_path)
               
        return render_template(output_page, pred_output = pred, user_image = file_path)
     
# For local system & cloud
if __name__ == "__main__":
    app.run(debug=True) 
