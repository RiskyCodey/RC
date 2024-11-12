from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, get_flashed_messages
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash 
from flask import jsonify

app = Flask(__name__, static_folder='static')
app.secret_key = 'lakbay2024'  

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'user29',
    'database': 'lakbay',
    'port': 3306,
    'auth_plugin': 'mysql_native_password'
}

@app.route('/')
def loginPage():
    return render_template('login.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route('/home')
def home(): 
    messages = get_flashed_messages()
    return render_template('home.html', messages=messages)
    
@app.route('/conditions')
def conditions():
    return render_template('conditions.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('loginPage'))

@app.route('/registerPage', methods=['GET', 'POST'])
def registerPage():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM userregister WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                return "Username or email already exists."
           
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO userregister (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed_password))
            conn.commit()
            return "Registration successful!"
        except mysql.connector.Error as err:
            return f"<script>alert('Error: {err}'); window.location.href='/registerPage';</script>"
        finally:
            cursor.close()
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM userregister WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user is not None:
            stored_hashed_password = user[3]

            if check_password_hash(stored_hashed_password, password):
                session['username'] = username
                app.logger.info(f"User '{username}' logged in successfully.")
                return jsonify({'redirect': url_for('profile')})
            else:
                app.logger.warning(f"Invalid password entered for username '{username}'.")
                return "Invalid username or password"
        else:
            app.logger.warning(f"No account found for username '{username}'.")
            return "No account found for this username"

    except mysql.connector.Error as err:
        app.logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error. Please try again later.'}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/profile_save', methods=['POST'])
def profile_save():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        birthday = request.form['birthday']
        primary_interest = request.form['primary_interest']
        secondary_interest = request.form['secondary_interest']
       
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM profiles WHERE firstname = %s AND lastname = %s", (firstname, lastname))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.execute("UPDATE profiles SET gender = %s, birthday = %s, primary_interest = %s, secondary_interest = %s WHERE id = %s",
                               (gender, birthday, primary_interest, secondary_interest, existing_user[0]))
                conn.commit()
            else:
                cursor.execute("INSERT INTO profiles (firstname, lastname, gender, birthday, primary_interest, secondary_interest) VALUES (%s, %s, %s, %s, %s, %s)",
                               (firstname, lastname, gender, birthday, primary_interest, secondary_interest))
                conn.commit()

            
            return render_template('profile.html', firstname=firstname, lastname=lastname,
                                   gender=gender, birthday=birthday,
                                   primary_interest=primary_interest,
                                   secondary_interest=secondary_interest)
        
        except mysql.connector.Error as err:
            app.logger.error(f"Error saving profile: {err}")
            return "An error occurred while saving profile."
        
        finally:
            cursor.close()
            conn.close()

@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)