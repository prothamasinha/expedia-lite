# Expedia Lite Design Note

## Frontend

The frontend is built with Vue.

It is responsible for:
- showing the hotel search input
- sending the search request
- displaying matching hotel information
- displaying available stays in a table
- showing a no-results message when no hotel matches

## FastAPI

FastAPI connects the Vue frontend to the Python backend.

It provides the search endpoint used by the frontend.

## Backend

The Python backend reads `hotels.csv` and `trips.csv`.

It searches hotel names and connects hotel records to trip records using `hotel_id`.

## Part 1 data flow

1. The user enters a hotel name.
2. Vue sends the hotel name to FastAPI.
3. Python searches `hotels.csv`.
4. Matching trips are found in `trips.csv` using `hotel_id`.
5. FastAPI returns the results.
6. Vue displays the hotel and available stays.