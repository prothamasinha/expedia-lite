from pydantic import BaseModel


class Hotel(BaseModel):
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float


class Trip(BaseModel):
    trip_id: str
    hotel_id: str
    trip_name: str
    check_in: str
    check_out: str


class User(BaseModel):
    user_id: str
    display_name: str


class Booking(BaseModel):
    booking_id: str
    user_id: str
    trip_id: str
    booked_on: str
    status: str


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


class BookingStatusUpdate(BaseModel):
    status: str