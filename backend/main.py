from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from controller import (
    create_booking,
    delete_booking,
    get_bookings,
    get_users,
    initialize_database,
    search_hotels,
    update_booking_status,
)
from models import BookingCreate, BookingStatusUpdate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()


@app.get("/")
def home():
    return {"message": "Expedia Lite backend is running"}


@app.get("/search")
def search(name: str):
    return search_hotels(name)


@app.get("/users")
def users():
    return get_users()


@app.get("/bookings")
def bookings():
    return get_bookings()


@app.post("/bookings")
def add_booking(booking: BookingCreate):
    try:
        booking_id = create_booking(
            booking.user_id,
            booking.trip_id,
        )

        return {
            "message": "Booking created",
            "booking_id": booking_id,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.put("/bookings/{booking_id}/status")
def change_booking_status(
    booking_id: str,
    update: BookingStatusUpdate,
):
    update_booking_status(
        booking_id,
        update.status,
    )

    return {
        "message": "Booking updated",
        "booking_id": booking_id,
        "status": update.status,
    }


@app.delete("/bookings/{booking_id}")
def remove_booking(booking_id: str):
    delete_booking(booking_id)

    return {
        "message": "Booking deleted",
        "booking_id": booking_id,
    }