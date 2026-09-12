# Expedia Lite

Expedia Lite is a small travel application created for IST 402 Assignment 1.

## Part 1

Part 1 allows a user to enter a hotel name and search the supplied hotel and trip data.

The application uses:

- Vue for the frontend
- Python for backend logic
- FastAPI for communication between the frontend and backend
- CSV files for Part 1 data

The backend reads `hotels.csv` and `trips.csv` and connects matching records using `hotel_id`.

## Run the backend

Open a terminal:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload