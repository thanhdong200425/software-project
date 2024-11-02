import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect,url_for

from database.database_function import add_new_record, count_all_records_from_table
from database.database_function import get_all_rooms
from database.database_function import get_db_connection

from helpers.validate import is_existing_data

app = Flask(__name__)

app.secret_key = os.urandom(24)


@app.route("/")
def index():
    bookings = [
        {
            "id": 1,
            "customer_name": "John Doe",
            "status": "Checked-in",
            "book_day": "2024-10-15",
            "expected_checkin": "2024-10-20",
            "expected_checkout": "2024-10-25",
            "actual_checkin": "2024-10-20",
            "checkout": None,
            "total_people": 2,
        },
        {
            "id": 2,
            "customer_name": "Jane Smith",
            "status": "Checked-out",
            "book_day": "2024-10-10",
            "expected_checkin": "2024-10-18",
            "expected_checkout": "2024-10-20",
            "actual_checkin": "2024-10-18",
            "checkout": "2024-10-20",
            "total_people": 1,
        },
        {
            "id": 3,
            "customer_name": "Alice Johnson",
            "status": "Checked-in",
            "book_day": "2024-10-12",
            "expected_checkin": "2024-10-21",
            "expected_checkout": "2024-10-28",
            "actual_checkin": "2024-10-21",
            "checkout": None,
            "total_people": 3,
        },
        {
            "id": 4,
            "customer_name": "Bob Brown",
            "status": "Reserved",
            "book_day": "2024-10-14",
            "expected_checkin": "2024-10-22",
            "expected_checkout": "2024-10-25",
            "actual_checkin": None,
            "checkout": None,
            "total_people": 2,
        },
        {
            "id": 5,
            "customer_name": "Emily White",
            "status": "Cancelled",
            "book_day": "2024-10-17",
            "expected_checkin": "2024-10-24",
            "expected_checkout": "2024-10-27",
            "actual_checkin": None,
            "checkout": None,
            "total_people": 0,
        },
        {
            "id": 5,
            "customer_name": "Emily White",
            "status": "Cancelled",
            "book_day": "2024-10-17",
            "expected_checkin": "2024-10-24",
            "expected_checkout": "2024-10-27",
            "actual_checkin": None,
            "checkout": None,
            "total_people": 0,
        },
        # Add more bookings here as needed
    ]
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_pages = (len(bookings) - 1) // per_page + 1

    # Get only the bookings for the current page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_bookings = bookings[start:end]

    return render_template(
        "index.html", bookings=paginated_bookings, page=page, total_pages=total_pages
    )


@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "GET":
        return render_template("booking.html")

    customer_name = request.form.get("customer-name")
    customer = is_existing_data("customer", "name", customer_name)
    if not customer:
        flash(
            "Username does not exist. Please try to enter another customer name",
            "error",
        )
        return redirect("/booking")

    room_name = request.form.get("room")
    room = is_existing_data("room", "name", room_name)
    if not room:
        flash(
            "Room name does not exist. Please try to enter another room name", "error"
        )
        return redirect("/booking")

    checkout_date = request.form.get("check-out-date")
    checkin_date = request.form.get("check-in-date")
    total_people = request.form.get("total-people")
    add_new_record(
        "booking",
        [
            "customer_id",
            "room_id",
            "status",
            "book_day",
            "expected_checkin",
            "expected_checkout",
            "total_people",
        ],
        (
            customer[0],
            room[0],
            "ongoing",
            datetime.now(),
            checkin_date,
            checkout_date,
            total_people,
        ),
    )
    flash("Added booking", "success")
    return redirect("/booking")




@app.route("/list_room", methods=["GET"])
def list_room():
    if request.method == "GET":
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
    port = int(os.environ.get("PORT", 5000))  # Use the PORT assigned by Heroku
    app.run(host="0.0.0.0", port=port, debug=True)
