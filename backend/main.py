from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import re
import requests

from dotenv import load_dotenv

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


# Load values from backend/.env
load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


app = FastAPI()


# Allow the Vue frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


initialize_database()


# --------------------------------------------------
# BASIC ROUTE
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "Expedia Lite backend is running"}


# --------------------------------------------------
# ASSIGNMENT 2 PART 1
# LIVE HOTEL SEARCH USING GEOAPIFY
# --------------------------------------------------

@app.get("/hotels/nearby")
def nearby_hotels(zip_code: str):

    # Make sure ZIP is exactly 5 digits.
    # This also preserves ZIP codes that begin with 0.
    if not re.fullmatch(r"\d{5}", zip_code):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid five-digit U.S. ZIP code.",
        )

    # Make sure the API key exists.
    if not GEOAPIFY_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Geoapify API key is not configured.",
        )

    try:
        # ------------------------------------------
        # STEP 1:
        # Convert ZIP code into latitude/longitude
        # ------------------------------------------

        geocode_response = requests.get(
            "https://api.geoapify.com/v1/geocode/search",
            params={
                "postcode": zip_code,
                "country": "United States of America",
                "type": "postcode",
                "filter": "countrycode:us",
                "format": "json",
                "limit": 5,
                "apiKey": GEOAPIFY_API_KEY,
            },
            timeout=10,
        )

        geocode_response.raise_for_status()

        geocode_data = geocode_response.json()

        matching_location = None

        # Do not silently use a different ZIP code.
        for result in geocode_data.get("results", []):
            result_postcode = str(result.get("postcode", ""))
            country_code = str(result.get("country_code", "")).lower()

            if (
                result_postcode == zip_code
                and country_code == "us"
            ):
                matching_location = result
                break

        if matching_location is None:
            raise HTTPException(
                status_code=404,
                detail="That U.S. ZIP code could not be resolved.",
            )

        latitude = matching_location.get("lat")
        longitude = matching_location.get("lon")

        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=404,
                detail="The ZIP code was found, but coordinates were unavailable.",
            )

        # ------------------------------------------
        # STEP 2:
        # Search for hotels within 5 kilometers
        # ------------------------------------------

        places_response = requests.get(
            "https://api.geoapify.com/v2/places",
            params={
                "categories": "accommodation.hotel",
                "filter": f"circle:{longitude},{latitude},5000",
                "bias": f"proximity:{longitude},{latitude}",
                "limit": 20,
                "apiKey": GEOAPIFY_API_KEY,
            },
            timeout=10,
        )

        places_response.raise_for_status()

        places_data = places_response.json()

        hotels = []

        # ------------------------------------------
        # STEP 3:
        # Clean up the Geoapify hotel information
        # ------------------------------------------

        for feature in places_data.get("features", []):
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            coordinates = geometry.get("coordinates", [])

            hotel_latitude = properties.get("lat")
            hotel_longitude = properties.get("lon")

            if len(coordinates) >= 2:
                hotel_longitude = coordinates[0]
                hotel_latitude = coordinates[1]

            hotel = {
                "place_id": properties.get("place_id"),
                "name": properties.get("name")
                or "Hotel name unavailable",
                "address": properties.get("formatted"),
                "city": properties.get("city"),
                "state": properties.get("state"),
                "postcode": properties.get("postcode"),
                "latitude": hotel_latitude,
                "longitude": hotel_longitude,
                "distance": properties.get("distance"),
            }

            hotels.append(hotel)

        # ------------------------------------------
        # STEP 4:
        # Send the results back to Vue
        # ------------------------------------------

        return {
            "zip_code": zip_code,
            "center": {
                "latitude": latitude,
                "longitude": longitude,
                "formatted": matching_location.get("formatted"),
            },
            "hotels": hotels,
        }

    except HTTPException:
        raise

    except requests.exceptions.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else 502
        )

        if status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Geoapify rate limit was reached. Please try again later.",
            )

        raise HTTPException(
            status_code=502,
            detail="Geoapify request failed.",
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Geoapify.",
        )


# --------------------------------------------------
# EXISTING EXPEDIA LITE ROUTES
# --------------------------------------------------

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