-- Customer table

CREATE TABLE customer
(
    id          integer primary key autoincrement,
    name        nvarchar not null,
    email       nvarchar,
    dob         date,
    credit_card text,
    address     text,
    company_id  integer
);

-- Room table
CREATE TABLE room
(
    id                  integer primary key autoincrement,
    room_name           text not null,
    type                text not null check ( type in ('standard', 'vip') ),
    status              text not null check ( status in ('available', 'ongoing', 'closed') ),
   

)

-- Thêm từng cột vào bảng room
ALTER TABLE room ADD COLUMN price_per_night FLOAT;
ALTER TABLE room ADD COLUMN service TEXT;
ALTER TABLE room ADD COLUMN description TEXT;
ALTER TABLE room ADD COLUMN capacity INTEGER;


-- Booking table
CREATE TABLE booking
(
    id                integer primary key autoincrement,
    customer_id       integer not null,
    room_id           integer not null,
    status            text    not null check ( status in ('ongoing', 'completed', 'cancelled') ),
    book_day          date    not null,
    expected_checkin  date    not null,
    expected_checkout date    not null,
    actual_checkin    date,
    actual_checkout   date,
    total_people      integer not null
);