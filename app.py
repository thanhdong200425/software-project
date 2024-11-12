import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect,url_for, session
from database.database_function import add_new_record
from database.database_function import get_all_rooms
from database.database_function import get_db_connection
from helpers.validate import is_existing_data
from functools import wraps
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

connection = sqlite3.connect("hotel1.db", timeout=10)
cursor = connection.cursor()
connection.commit()
connection.close()

def login_required(f):
    @wraps(f)
    def check(*args, **kwargs):
        if not session.get('loggedin'):
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return check

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect("hotel1.db") as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, hashed_password))
            user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['userid'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            
            if "next" in request.args:
                return redirect(request.args['next'])
                
            return redirect("/")
        else:
            mesage = 'Please enter correct email / password!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
app.secret_key = os.urandom(24)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        email = request.form['email']
        
        with sqlite3.connect("hotel1.db") as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
            account = cursor.fetchone()

            if account:
                mesage = 'Account already exists!'
            elif not userName or not password or not email:
                mesage = 'Please fill out the form!'
            else:
                cursor.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (userName, email, password))
                conn.commit()
                mesage = 'You have successfully registered!'
                return render_template('login.html')
    elif request.method == 'POST':
        mesage = 'Please fill out the form!'
    return render_template('register.html')

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    if request.method == "GET":
        return render_template("booking.html")

    customer_name = request.form.get("customer-name")
    customer = is_existing_data("customer", "name", customer_name)
    if not customer:
        flash("Username does not exist. Please try to enter another customer name", "error")
        return redirect("/booking")

    room_name = request.form.get("room")
    room = is_existing_data("room", "name", room_name)
    if not room:
        flash("Room name does not exist. Please try to enter another room name", "error")
        return redirect("/booking")

    checkout_date = request.form.get("check-out-date")
    checkin_date = request.form.get("check-in-date")
    total_people = request.form.get("total-people")
    add_new_record(
        "booking",
        ["customer_id", "room_id", "status", "book_day", "expected_checkin", "expected_checkout", "total_people"],
        (customer[0], room[0], "ongoing", datetime.now(), checkin_date, checkout_date, total_people)
    )
    flash("Added booking", "success")
    return redirect("/booking")

@app.route("/list_room", methods=["GET"])
@login_required
def list_room():
    rooms = get_all_rooms()
    return render_template("list_room.html", rooms=rooms)





@app.route('/rooms')
def list_rooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM room').fetchall()
    conn.close()
    return render_template('list_room.html', rooms=rooms)

@app.route('/list_room/create', methods=['GET', 'POST'])
def create_room():
    if request.method == 'POST':
        room_name = request.form['name']
        room_type = request.form['type']
        price = request.form['price_per_night']
        service = request.form['service']
        description = request.form['description']
        capacity = request.form['capacity']
        status = request.form['status']

        conn = get_db_connection()
        conn.execute('INSERT INTO room (name, type, price_per_night, service, description, capacity, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (room_name, room_type, price, service, description, capacity, status))
        conn.commit()
        conn.close()
        flash('Room added successfully!')
        return redirect(url_for('list_rooms'))

    return render_template('create_room.html')

@app.route('/list_room/edit/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    conn = get_db_connection()
    room = conn.execute('SELECT * FROM room WHERE id = ?', (room_id,)).fetchone()

    if request.method == 'POST':
        room_name = request.form['name']
        room_type = request.form['type']
        price = request.form['price_per_night']
        service = request.form['service']
        description = request.form['description']
        capacity = request.form['capacity']
        status = request.form['status']

        if status not in ['available', 'ongoing', 'closed']:
            flash('Invalid status value.', 'error')
            return redirect(url_for('edit_room', room_id=room_id))

        conn.execute('UPDATE room SET name = ?, type = ?, price_per_night = ?, service = ?, description = ?, capacity = ?, status = ? WHERE id = ?',
                     (room_name, room_type, price, service, description, capacity, status, room_id))
        conn.commit()
        conn.close()
        flash('Room updated successfully!')
        return redirect(url_for('list_rooms'))

    conn.close()
    return render_template('edit_room.html', room=room)

@app.route('/rooms/delete/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM room WHERE id = ?', (room_id,))
    conn.commit()
    conn.close()
    flash('Room deleted successfully!')
    return redirect(url_for('list_rooms'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
