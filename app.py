import os
import redis
from datetime import datetime
from typing import final

from flask import Flask, render_template, request, flash, redirect, url_for, session
from database.database_function import add_new_record, fetch_data_from_table
from database.database_function import get_db_connection
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = redis.Redis(
    host='redis-11725.c257.us-east-1-3.ec2.redns.redis-cloud.com',
    port=11725,
    password='fzcGxR1euqu8l4Tw8J0zYETbBWYGNilA')


@app.before_request
def check_authentication():
    if request.endpoint not in ['login', 'register'] and not session.get("logged_in"):
        return redirect(url_for("login"))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = conn.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, hashed_password)).fetchone()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['userid']
            session['email'] = user['email']
            session['customer_name'] = user['name']
            conn.execute(
                """
                UPDATE customer
                SET name = ?
                WHERE customer_id = ?
                """,
                (user['name'], user['userid'])
            )
            conn.commit()
            conn.close()
            return redirect('/')
        else:
            flash("Login information is wrong", "error")
            # return redirect('/login')

    return render_template('login.html')



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        username = request.form["name"]
        password = request.form['password']
        email = request.form["email"]

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = fetch_data_from_table(table="user", column="*", condition="email = ? AND password = ?",
                                     condition_params=(email, hashed_password), fetch_one=True)
        if user:
            message = "Account already exists!"
            return render_template("register.html", message=message)
        elif not username or not password or not email:
            message = "Please fill out the form!"
            return render_template("register.html", message=message)
        else:
            # Add a new user into database
            add_new_record(table="user", column=["name", "email", "password"], params=(username, email, hashed_password))
            message = "You have successfully registered!"
            return render_template("login.html", message=message)

    return render_template("register.html")

@app.route("/")
def index():
    conn = get_db_connection()
    bookings = conn.execute("""
        SELECT booking.booking_id AS id, customer.name AS customer_name, booking.status,
               booking.book_day, booking.expected_checkin, booking.expected_checkout,
               booking.actual_checkin, booking.actual_checkout, booking.total_people
        FROM booking
        JOIN customer ON booking.customer_id = customer.customer_id
        ORDER BY booking.book_day ASC
    """).fetchall()
    conn.close()

    page, per_page = request.args.get("page", 1, type=int), 5
    paginated_bookings = bookings[(page - 1) * per_page : page * per_page]
    total_pages = (len(bookings) - 1) // per_page + 1

    return render_template("index.html", bookings=paginated_bookings, page=page, total_pages=total_pages)

@app.route('/booking', methods=['POST', 'GET'])
def booking():
    if 'user_id' not in session:
        flash("Login for booking.", "error")
        # return redirect('/login')

    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customer").fetchall()
    rooms = conn.execute("SELECT * FROM room WHERE status = 'available'").fetchall()
    conn.close()

    customer_name = session.get("customer_name")

    if request.method == 'POST':
        room_id = request.form['room_id']
        customer_name = request.form['customer-name']
        checkin_date = request.form['check-in-date']
        checkout_date = request.form['check-out-date']
        total_people = request.form['total-people']

        conn = get_db_connection()
        customer = conn.execute(
            "SELECT customer_id FROM customer WHERE name = ?", (customer_name,)
        ).fetchone()

        if not customer:
            flash("Customer does not exist or is invalid.", "error")
            conn.close()
            return redirect('/booking')
        
        customer_id = customer['customer_id']

        # Kiểm tra xem phòng có tồn tại và còn trống hay không
        room_exists = conn.execute(
            "SELECT 1 FROM room WHERE room_id = ? AND status = 'available'", (room_id,)
        ).fetchone()
        if not room_exists:
            flash("Room does not exist or is already booked.", "error")
            conn.close()
            return redirect('/booking')

        conn.execute("""
            INSERT INTO booking (customer_id, room_id, status, book_day, expected_checkin, expected_checkout, total_people)
            VALUES (?, ?, 'ongoing', CURRENT_DATE, ?, ?, ?)
        """, (customer_id, room_id, checkin_date, checkout_date, total_people))

        conn.commit()
        conn.close()

        flash("Booking success!", "success")
        return redirect('/booking')

    return render_template('booking.html', customers=customers, rooms=rooms, customer_name=customer_name)



@app.route('/customer', methods=["GET"])
def customer():
    try:
        conn = get_db_connection()
        customers = conn.execute("""SELECT *
                                    FROM customer""").fetchall()
        conn.close()

        if not customers:
            flash("No customer data!", "error")
            return redirect(url_for('index'))

        return render_template('customer.html', customers=customers)

    except Exception as e:
        flash(f"An error has occurred: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'user_id' not in session:
        flash("Please login.", "error")
        # return redirect(url_for('login'))

    conn = get_db_connection()

    customer = conn.execute("SELECT * FROM customer WHERE customer_id = ?", (session['user_id'],)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        dob = request.form["dob"]
        credit_card = request.form["credit_card"]
        address = request.form["address"]
        company_id = request.form["company_id"]

        if customer:
            conn.execute(
                """
                UPDATE customer
                SET name = ?, email = ?, dob = ?, credit_card = ?, address = ?, company_id = ?
                WHERE customer_id = ?
                """,
                (name, email, dob, credit_card, address, company_id, session['user_id'])
            )
            flash("Updated information successfully!", "success")
        else:
            add_new_record(
                table="customer",
                column=["name", "email", "dob", "address", "credit_card", "company_id"],
                params=(name, email, dob, address, credit_card, company_id)
            )
            flash("New customer account created!", "success")

        conn.commit()
        conn.close()
        session['customer_name'] = name
        return redirect(url_for("customer"))

    conn.close()
    return render_template('profile.html', customer=customer)

@app.route("/list_room", methods=["GET"])
def list_room():
    conn = get_db_connection()
    rooms = conn.execute("SELECT * FROM room").fetchall()
    conn.close()
    return render_template("list_room.html", rooms=rooms)


@app.route("/list_room/create", methods=["GET", "POST"])
def create_room():
    if request.method == "POST":
        room_name = request.form["room_name"]
        room_type = request.form["type"]
        price = request.form["price_per_night"]
        service = request.form["service"]
        description = request.form["description"]
        capacity = request.form["capacity"]
        status = request.form["status"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO room (room_name, type, price_per_night, service, description, capacity, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (room_name, room_type, price, service, description, capacity, status),
        )
        conn.commit()
        conn.close()
        # flash("Room added successfully!")
        return redirect(url_for("list_room"))

    return render_template('CRUD_Room/create_room.html')


@app.route("/list_room/edit/<int:room_id>", methods=["GET", "POST"])
def edit_room(room_id):
    conn = get_db_connection()
    room = conn.execute("SELECT * FROM room WHERE room_id = ?", (room_id,)).fetchone()

    if request.method == "POST":
        room_name = request.form["room_name"]
        room_type = request.form["type"]
        price = request.form["price_per_night"]
        service = request.form["service"]
        description = request.form["description"]
        capacity = request.form["capacity"]
        status = request.form["status"]

        if status not in ["available", "ongoing", "closed"]:
            flash("Invalid status value.", "error")
            return redirect(url_for("edit_room", room_id=room_id))

        conn.execute(
            "UPDATE room SET room_name = ?, type = ?, price_per_night = ?, service = ?, description = ?, capacity = ?, status = ? WHERE room_id = ?",
            (
                room_name,
                room_type,
                price,
                service,
                description,
                capacity,
                status,
                room_id,
            ),
        )
        conn.commit()
        conn.close()
        # flash("Room updated successfully!")
        return redirect(url_for("list_room"))

    conn.close()
    return render_template('CRUD_Room/edit_room.html', room=room)


@app.route("/rooms/delete/<int:room_id>", methods=["POST"])
def delete_room(room_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM room WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()
    # flash("Room deleted successfully!")
    return redirect(url_for("list_room"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)