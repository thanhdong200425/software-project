import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect

from database.database_function import add_new_record
from helpers.validate import is_existing_data

app = Flask(__name__)


app.secret_key = os.urandom(24)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        return render_template("booking.html")

    customer_name = request.form.get("customer-name")
    customer = is_existing_data('customer', 'name', customer_name)
    if not customer:
        flash('Username does not exist. Please try to enter another customer name', 'error')
        return redirect("/booking")

    room_name = request.form.get("room")
    room = is_existing_data('room', 'name', room_name)
    if not room:
        flash('Room name does not exist. Please try to enter another room name', 'error')
        return redirect('/booking')

    checkout_date = request.form.get('check-out-date')
    checkin_date = request.form.get('check-in-date')
    total_people = request.form.get('total-people')
    add_new_record('booking', ['customer_id', 'room_id', 'status', 'book_day', 'expected_checkin', 'expected_checkout', 'total_people'], (customer[0], room[0], 'ongoing', datetime.now(), checkin_date, checkout_date, total_people))
    flash("Added booking", 'success')
    return redirect('/booking')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use the PORT assigned by Heroku
    app.run(host="0.0.0.0", port=port, debug=True)
