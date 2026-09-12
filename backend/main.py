import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


def read_csv(filename):
    file_path = BASE_DIR / filename

    with open(file_path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


@app.get("/")
def home():
    return {"message": "Expedia Lite backend is running"}


@app.get("/search")
def search_hotels(name: str):
    hotels = read_csv("hotels.csv")
    trips = read_csv("trips.csv")

    matches = []

    for hotel in hotels:
        if name.lower() in hotel["hotel_name"].lower():

            hotel_trips = [
                trip
                for trip in trips
                if trip["hotel_id"] == hotel["hotel_id"]
            ]

            matches.append(
                {
                    "hotel": hotel,
                    "trips": hotel_trips,
                }
            )

    return matches