import csv
import sqlite3
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expedia_lite.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def read_csv(filename):
    with open(BASE_DIR / filename, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            hotel_id TEXT PRIMARY KEY,
            hotel_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            nightly_rate_usd REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id TEXT PRIMARY KEY,
            hotel_id TEXT NOT NULL,
            trip_name TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            trip_id TEXT NOT NULL,
            booked_on TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM hotels")
    if cursor.fetchone()[0] == 0:
        for hotel in read_csv("hotels.csv"):
            cursor.execute(
                """
                INSERT INTO hotels
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    hotel["hotel_id"],
                    hotel["hotel_name"],
                    hotel["city"],
                    hotel["state"],
                    hotel["nightly_rate_usd"],
                ),
            )

        for trip in read_csv("trips.csv"):
            cursor.execute(
                """
                INSERT INTO trips
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    trip["trip_id"],
                    trip["hotel_id"],
                    trip["trip_name"],
                    trip["check_in"],
                    trip["check_out"],
                ),
            )

        for user in read_csv("users.csv"):
            cursor.execute(
                """
                INSERT INTO users
                VALUES (?, ?)
                """,
                (
                    user["user_id"],
                    user["display_name"],
                ),
            )

        for booking in read_csv("bookings.csv"):
            cursor.execute(
                """
                INSERT INTO bookings
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    booking["booking_id"],
                    booking["user_id"],
                    booking["trip_id"],
                    booking["booked_on"],
                    booking["status"],
                ),
            )

    connection.commit()
    connection.close()


def search_hotels(name):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            h.hotel_id,
            h.hotel_name,
            h.city,
            h.state,
            h.nightly_rate_usd,
            t.trip_id,
            t.trip_name,
            t.check_in,
            t.check_out
        FROM hotels h
        LEFT JOIN trips t ON h.hotel_id = t.hotel_id
        WHERE LOWER(h.hotel_name) LIKE LOWER(?)
        """,
        (f"%{name}%",),
    ).fetchall()

    connection.close()

    hotels = {}

    for row in rows:
        hotel_id = row["hotel_id"]

        if hotel_id not in hotels:
            hotels[hotel_id] = {
                "hotel": {
                    "hotel_id": row["hotel_id"],
                    "hotel_name": row["hotel_name"],
                    "city": row["city"],
                    "state": row["state"],
                    "nightly_rate_usd": row["nightly_rate_usd"],
                },
                "trips": [],
            }

        if row["trip_id"]:
            hotels[hotel_id]["trips"].append(
                {
                    "trip_id": row["trip_id"],
                    "hotel_id": row["hotel_id"],
                    "trip_name": row["trip_name"],
                    "check_in": row["check_in"],
                    "check_out": row["check_out"],
                }
            )

    return list(hotels.values())


def get_users():
    connection = get_connection()
    rows = connection.execute("SELECT * FROM users").fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_bookings():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            b.booking_id,
            b.user_id,
            u.display_name,
            b.trip_id,
            t.trip_name,
            h.hotel_name,
            b.booked_on,
            b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN trips t ON b.trip_id = t.trip_id
        JOIN hotels h ON t.hotel_id = h.hotel_id
        ORDER BY b.booking_id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def create_booking(user_id, trip_id):
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        "SELECT booking_id FROM bookings"
    ).fetchall()

    numbers = [
        int(row["booking_id"][1:])
        for row in rows
        if row["booking_id"].startswith("B")
    ]

    next_number = max(numbers, default=0) + 1
    booking_id = f"B{next_number:03d}"

    cursor.execute(
        """
        INSERT INTO bookings
        (booking_id, user_id, trip_id, booked_on, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            booking_id,
            user_id,
            trip_id,
            date.today().isoformat(),
            "confirmed",
        ),
    )

    connection.commit()
    connection.close()

    return booking_id


def update_booking_status(booking_id, status):
    connection = get_connection()

    connection.execute(
        """
        UPDATE bookings
        SET status = ?
        WHERE booking_id = ?
        """,
        (status, booking_id),
    )

    connection.commit()
    connection.close()


def delete_booking(booking_id):
    connection = get_connection()

    connection.execute(
        """
        DELETE FROM bookings
        WHERE booking_id = ?
        """,
        (booking_id,),
    )

    connection.commit()
    connection.close()