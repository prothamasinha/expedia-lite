# IST 402 — Assignment 2 Part 1
## Live Hotel Search and Map

## 1. Project Access

**Repository:**  
https://github.com/prothamasinha/expedia-lite

**Assessed Commit:**  
aaad65806e9c812244e65b6ed1b9a387c951ef05

### Startup and Configuration Instructions

#### Backend

1. Open a terminal in the project folder.
2. Navigate to the backend folder:

```bash
cd backend
```

3. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

The Geoapify API key is stored locally in `backend/.env` using:

```text
GEOAPIFY_API_KEY=your_key_here
```

The `.env` file is ignored by Git and is not committed to the repository.

#### Frontend

1. Open another terminal.
2. Navigate to the frontend folder:

```bash
cd frontend
```

3. Start the Vue application:

```bash
npm run dev
```

4. Open the local URL displayed by Vite, normally:

```text
http://localhost:5173
```

---

## 2. Research Notes

Before implementation, I reviewed the Geoapify Geocoding API, Geoapify Places API, and Leaflet documentation.

### Sources Consulted

- Geoapify Geocoding API: https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/
- Geoapify Places API: https://apidocs.geoapify.com/docs/places/
- Leaflet documentation: https://leafletjs.com/reference.html

### What I Learned

Geoapify's geocoding API can resolve a U.S. ZIP code into latitude and longitude coordinates. I used the returned ZIP location as the center of the hotel search instead of using the user's current location.

The Geoapify Places API can search for hotel locations within a geographic radius. For this project, the backend searches within 5 km of the ZIP-code center.

Leaflet provides an interactive map that can display returned hotel locations using markers and popups.

One important design concern was making sure the application only displays information that is actually available from the provider. Geoapify provides place and location information, so I did not add invented hotel prices, ratings, room availability, or booking confirmations.

### Design Decisions

Based on the research, I designed the application so that:

- users enter a five-digit U.S. ZIP code;
- Geoapify requests go through the FastAPI backend;
- the Geoapify API key stays in the backend `.env` file;
- hotel results appear in both a list and a Leaflet map;
- clicking a hotel in the list identifies the same hotel on the map;
- clicking a map marker identifies the same hotel in the list;
- hotel names, addresses, coordinates, and distances come from the provider data;
- invalid input, unresolved ZIP codes, loading, empty results, and request failures have separate interface states.

---

## 3. Early Mockup


Before implementation, the planned interface used a ZIP-code search at the top with hotel results and a map as the main content.

During implementation, I kept that basic structure but adjusted the layout so the hotel list and Leaflet map could be viewed side by side. I also added clearer feedback for invalid ZIP codes, unresolved ZIP codes, loading, empty results, and failed requests.

---

## 4. Screen-Recorded Demo

**Demo Video:**  
https://drive.google.com/file/d/1CS0eVjHkfNUn6F7-1nP-xIRPU-iojN2o/view?usp=sharing

The demonstration shows:

- entering ZIP code `16802`;
- Geoapify returning nearby hotels;
- hotel results appearing in a list and on a Leaflet map;
- selecting Scholar Hotel State College from the list and seeing its map popup;
- selecting Nittany Lion Inn from the map and seeing the matching list item selected;
- invalid ZIP handling;
- unresolved ZIP handling;
- failed-request handling.

---

## 5. Verification Record

**Live Search ZIP Tested:** `16802`  
**Observation Date:** September 29, 2026

### Test 1 — Valid ZIP Search

**Input:**  
`16802`

**Expected Result:**  
The backend should resolve the requested U.S. ZIP code and use that returned location as the center of a hotel search within 5 km.

**Observed Result:**  
The ZIP resolved to State College, Pennsylvania. Geoapify returned 20 nearby hotel results. The results appeared in both the hotel list and the Leaflet map.

Examples included Scholar Hotel State College, Hotel State College, Nittany Lion Inn, Hyatt Place State College, and Graduate by Hilton State College.

**Result:** Pass

### Test 2 — List to Map Synchronization

**Action:**  
Clicked Scholar Hotel State College in the hotel list.

**Expected Result:**  
The corresponding hotel should be identified on the map.

**Observed Result:**  
The map moved to Scholar Hotel State College and opened its popup. The hotel remained selected in the list.

**Result:** Pass

### Test 3 — Map to List Synchronization

**Action:**  
Clicked the Nittany Lion Inn marker on the map.

**Expected Result:**  
The corresponding hotel should be identified in the hotel list.

**Observed Result:**  
The Nittany Lion Inn popup opened and the corresponding hotel card became selected in the list.

**Result:** Pass

### Test 4 — Invalid ZIP Input

**Input:**  
`123`

**Expected Result:**  
The application should reject the input instead of performing a hotel search.

**Observed Result:**  
The application displayed:

`Please enter a valid five-digit U.S. ZIP code.`

**Result:** Pass

### Test 5 — Unresolved ZIP

**Input:**  
`00000`

**Expected Result:**  
The application should report that the ZIP cannot be resolved and should not silently search a different location.

**Observed Result:**  
The application displayed:

`That U.S. ZIP code could not be resolved.`

**Result:** Pass

### Test 6 — Failed Request

**Action:**  
Stopped the FastAPI backend and attempted another search for `16802`.

**Expected Result:**  
The application should report a failed request instead of describing the situation as an empty successful search.

**Observed Result:**  
The application displayed:

`The request could not be completed. Please try again.`

**Result:** Pass

### Test 7 — Credential Protection

**Action:**  
Ran:

```bash
git check-ignore -v .env
```

**Expected Result:**  
The local `.env` file should be ignored by Git.

**Observed Result:**  
Git reported that `.env` was covered by `.gitignore`.

**Result:** Pass

### Test 8 — Dependency Check and Verification

Before adding dependencies, I checked the existing project environment.

For the backend, `requests` and `python-dotenv` were not installed in the project virtual environment. After reviewing why they were required and approving the installation, both were installed.

For the frontend, I ran:

```bash
npm list leaflet
```

The first check showed that Leaflet was not installed. After approving the installation, Leaflet was installed and verified as version `1.9.4`.

**Result:** Pass

### Remaining Limitations

Live hotel results depend on Geoapify's current provider data, so the number and details of returned hotels may change.

The application does not claim that the returned list contains every hotel in the area.

Geoapify supplies place information rather than confirmed booking information. Therefore, the application does not invent nightly prices, ratings, room availability, or booking confirmations.

A dedicated simulated no-results case was not completed during the recorded verification session. The frontend includes a separate empty-results state for a successful response containing no hotels.

---

## 6. AI Disclosure and Evidence Log

**AI Tool:** ChatGPT  
**Model:** GPT-5.6 Sol

I used ChatGPT as a development assistant while completing Assignment 2 Part 1. I reviewed and tested suggested changes before including them in the project.

### Use 1 — Backend API Integration

**Prompt excerpt:**  
"just rewrite the whole thing"

**Use:**  
ChatGPT helped revise `backend/main.py` so FastAPI could accept a five-digit ZIP code, resolve the ZIP through Geoapify, validate that the returned U.S. postcode matched the requested ZIP, and search for hotels within 5 km.

**Related Change:**  
`backend/main.py`

### Use 2 — Frontend and Leaflet Integration

**Prompt excerpt:**  
"then"

**Use:**  
ChatGPT helped revise `frontend/src/App.vue` to provide ZIP-code search, hotel results, a Leaflet map, and synchronized list and map selection.

**Related Change:**  
`frontend/src/App.vue`

### Use 3 — Dependency Process

**Prompt excerpt:**  
"im confused what should i do next"

**Use:**  
ChatGPT helped me follow the required CHECK, TAKE ACTION, and VERIFY process for project dependencies.

I first checked whether `requests`, `python-dotenv`, and Leaflet were already installed. The proposed installations were explained before I approved them. After installation, I verified the packages again.

**Related Changes:**  
Backend Python environment and frontend npm dependencies.

### Failed or Revised Approach

**Initial Approach:**  
The existing Expedia Lite application searched supplied local hotel records by hotel name and included traveler and booking functionality.

**Problem:**  
Entering `16802` produced `No matching hotels found` because the application was still using the older local hotel search instead of the new live Geoapify workflow. The interface also did not include the required map.

**Revision:**  
I added a new FastAPI hotel-discovery endpoint that uses Geoapify for ZIP geocoding and nearby hotel searches. I then revised the Vue interface to search by ZIP code and display synchronized hotel results in a list and Leaflet map.

**Result:**  
The revised application successfully resolved `16802`, returned live nearby hotel information from Geoapify, displayed the results on the map and in the list, and passed the tested input and request-failure cases.