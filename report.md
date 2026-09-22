# Expedia Lite — Part 2

## Repository and commit

GitHub repository: https://github.com/prothamasinha/expedia-lite

Part 1 commit:
d70d223f93025a3211fea2b4549ef8173e6205af

Part 2 commit:
71f5ed2360707524997f6c622e2af75b2d6873ef

## Implementation

Part 2 expands Expedia Lite from a CSV-based hotel search application into a persistent booking application using SQLite.

The Vue frontend allows users to search for hotels, select a demo traveler, create bookings, view booking history, cancel bookings, and delete test bookings.

FastAPI handles communication between the Vue frontend and the Python backend.

The backend uses SQLite for persistence. The starter hotel, trip, user, and booking data is seeded into the database, and application reads and writes use SQLite after initialization.

The application follows an MVC-style structure:

- Models define the application data structures.
- Vue acts as the View and presents the interface.
- The database controller performs SQLite CRUD operations.
- FastAPI connects the frontend to the backend.

## CRUD functionality

### Create

A user can select a traveler, search for a hotel, and click Book on an available trip.

A new booking is assigned a unique booking ID and saved to SQLite.

### Read

Booking History displays bookings stored in SQLite, including the traveler, hotel, trip, and current status.

### Update

A confirmed booking can be cancelled through the frontend.

Cancelling changes the booking status to `cancelled` while keeping the booking record in history.

### Delete

A test booking can be deleted through the frontend.

The deleted booking is removed from SQLite and disappears from Booking History.

## Verification

I manually reviewed the Part 2 changes in VS Code and tested the application in the browser.

### Create booking

Action:
Selected a demo traveler, searched for Harbor Lantern Hotel, and clicked Book on an available trip.

Expected result:
A new confirmed booking should be created and appear in Booking History.

Observed result:
The new booking appeared successfully in Booking History.

### Read booking history

Action:
Opened the application and viewed Booking History.

Expected result:
Bookings stored in SQLite should appear with traveler, hotel, trip, and status information.

Observed result:
The seeded and newly created bookings displayed successfully.

### Update booking

Action:
Clicked Cancel on a confirmed booking.

Expected result:
The booking should remain in Booking History but its status should change to cancelled.

Observed result:
The booking remained visible and its status changed to `cancelled`.

### Delete booking

Action:
Clicked Delete on a test booking.

Expected result:
The booking should be removed from Booking History and the SQLite database.

Observed result:
The booking disappeared successfully.

### Persistence

Action:
Refreshed the browser and restarted the application.

Expected result:
Saved database changes should remain and starter records should not be duplicated.

Observed result:
Booking History loaded successfully from SQLite and persisted records remained available.

## Demo video

Part 2 demo video:
https://drive.google.com/file/d/1aLyAHXxhLgLYScS7uxbiFdUhGFnCBIGx/view?usp=sharing

The demo is under three minutes and shows the application performing Create, Read, Update, and Delete operations through the frontend.

## Project context and next steps

README:
https://github.com/prothamasinha/expedia-lite/blob/main/README.md

AGENTS.md:
https://github.com/prothamasinha/expedia-lite/blob/main/AGENTS.md

Design note:
https://github.com/prothamasinha/expedia-lite/blob/main/docs/design.md

Selected prompts:
https://github.com/prothamasinha/expedia-lite/blob/main/prompts/part1-prompts.md

Current handoff:
https://github.com/prothamasinha/expedia-lite/blob/main/handoffs/current.md

Remaining limitations:
The application uses simulated travelers and local SQLite persistence. The optional authentication and surge-pricing bonus features were not implemented.

Next task:
Continue improving interface usability and application validation.