# IST 402 — Assignment 2 Part 1
## Live Hotel Search and Map

### 1. Project Access
**Repository:**  
https://github.com/prothamasinha/expedia-lite

**Assessed Commit:**  
8f9a4e0cc77ee25f6f7a05d61d082b0a7759576d

### Startup and Configuration Instructions

#### Backend

1. Open a terminal in the project folder.
2. Navigate to the backend folder:

```bash
cd backend

## 2. Research Notes

Before implementation, I reviewed the Geoapify Geocoding API, Geoapify Places API, and Leaflet documentation.

### Sources Consulted

- Geoapify Geocoding API: https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/
- Geoapify Places API: https://apidocs.geoapify.com/docs/places/
- Leaflet documentation: https://leafletjs.com/reference.html

### What I Learned

Geoapify's geocoding API can resolve a U.S. ZIP code into latitude and longitude coordinates. I used the returned ZIP location as the center of the hotel search rather than using the user's current location.

The Geoapify Places API can search for hotel locations within a geographic radius. I used a 5 km radius around the ZIP-code center as required by the assignment.

Leaflet provides an interactive map that can display hotel locations with markers and popups.

### Design Decisions

Based on the research, I designed the application so that:

- the user enters a five-digit U.S. ZIP code;
- hotel data is requested through the FastAPI backend;
- the Geoapify API key stays in the backend `.env` file;
- hotel results appear in both a list and a Leaflet map;
- clicking a hotel in the list identifies the same hotel on the map;
- clicking a marker on the map identifies the same hotel in the list;
- the application displays only information actually returned by Geoapify;
- prices, ratings, room availability, and booking claims are not invented;
- invalid ZIP codes, unresolved ZIP codes, empty results, loading states, and request failures are handled separately.

## 3. Early Mockup

Before implementation, I created an early design showing the planned ZIP-code search, hotel results list, and map layout.

**Mockup:**  
[ADD MOCKUP IMAGE OR LINK HERE]

The original design focused on a simple search-first layout. During implementation, I kept the same basic idea but adjusted the spacing and result layout so the hotel list and Leaflet map could be viewed side by side. I also added clear messages for invalid ZIP codes, unresolved ZIP codes, loading, empty results, and failed requests.

## 4. Screen-Recorded Demo

**Demo Video:**  
[ADD VIDEO LINK HERE]

The demo shows:

- entering ZIP code `16802`;
- Geoapify returning nearby hotels;
- the hotels appearing in a list and on the Leaflet map;
- selecting Scholar Hotel State College from the list and seeing the corresponding map popup;
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
The backend should resolve the ZIP code to the intended U.S. postcode location and search for hotels within 5 km of that point.

**Observed Result:**  
The ZIP resolved to State College, Pennsylvania. Geoapify returned 20 nearby hotel results, including Scholar Hotel State College, Hotel State College, Nittany Lion Inn, Hyatt Place State College, and others. The hotels appeared in both the list and the Leaflet map.

**Result:** Pass

### Test 2 — List to Map Synchronization

**Action:**  
Clicked Scholar Hotel State College in the hotel list.

**Expected Result:**  
The same hotel should be identified on the map.

**Observed Result:**  
The map moved to Scholar Hotel State College and opened its popup.

**Result:** Pass

### Test 3 — Map to List Synchronization

**Action:**  
Clicked the Nittany Lion Inn marker on the map.

**Expected Result:**  
The corresponding hotel should be identified in the list.

**Observed Result:**  
The Nittany Lion Inn popup opened and the matching hotel card in the list became selected.

**Result:** Pass

### Test 4 — Invalid ZIP

**Input:**  
`123`

**Expected Result:**  
The application should reject the input before performing a search.

**Observed Result:**  
The application displayed: `Please enter a valid five-digit U.S. ZIP code.`

**Result:** Pass

### Test 5 — Unresolved ZIP

**Input:**  
`00000`

**Expected Result:**  
The application should not silently search a different location.

**Observed Result:**  
The application displayed: `That U.S. ZIP code could not be resolved.`

**Result:** Pass

### Test 6 — Failed Request

**Action:**  
Stopped the FastAPI backend and attempted a search for `16802`.

**Expected Result:**  
The application should display a request failure instead of saying that no hotels were found.

**Observed Result:**  
The application displayed: `The request could not be completed. Please try again.`

**Result:** Pass

### Test 7 — Credential Protection

**Action:**  
Used `git check-ignore -v .env`.

**Expected Result:**  
The `.env` file should be ignored by Git.

**Observed Result:**  
Git reported that `.env` is ignored through `.gitignore`.

**Result:** Pass

### Test 8 — Dependency Verification

Before installing new dependencies, the existing environment was checked.

For the backend, `requests` and `python-dotenv` were initially not installed in the project virtual environment. After approval, they were installed and verified.

For the frontend, Leaflet was checked with:

`npm list leaflet`

It was not installed. After approval, Leaflet was installed and verified as version `1.9.4`.

**Result:** Pass

### Remaining Limitations

The live hotel results depend on Geoapify's current provider data, so the number and details of returned hotels may change over time.

The application does not claim that the results are a complete inventory of every hotel in the area.

Geoapify provides location information, so the application does not invent hotel prices, ratings, room availability, or booking confirmation.

---

## 6. AI Disclosure and Evidence Log

**AI Tool:** ChatGPT  
**Model:** GPT-5.6 Sol

I used ChatGPT as a development assistant while completing Assignment 2 Part 1.

### Use 1 — Backend API Integration

**Prompt excerpt:**  
"just rewrite the whole thing"

**Use:**  
ChatGPT helped me revise `main.py` so FastAPI could accept a five-digit ZIP code, use Geoapify to resolve the ZIP location, and request nearby hotels within 5 km.

**Related change:**  
`backend/main.py`

### Use 2 — Frontend and Leaflet Integration

**Prompt excerpt:**  
"then"

**Use:**  
ChatGPT helped me update `App.vue` to display hotel results in a list and on a Leaflet map and synchronize selection between the two.

**Related change:**  
`frontend/src/App.vue`

### Use 3 — Dependency Check and Installation

**Prompt excerpt:**  
"im confused what should i do next"

**Use:**  
ChatGPT helped me follow the CHECK, TAKE ACTION, and VERIFY process before installing `requests`, `python-dotenv`, and Leaflet.

**Related changes:**  
Backend virtual environment and frontend npm dependencies.

### Failed or Revised Approach

**Initial approach:**  
The existing Expedia Lite application searched local hotel records by hotel name and included booking-related features.

**Problem:**  
Searching `16802` produced `No matching hotels found` because the application was still using the older local search functionality instead of live Geoapify data.

**Revision:**  
I added a new FastAPI route that resolves ZIP codes through Geoapify and searches nearby hotels. I then replaced the frontend search interface with ZIP-code search and a synchronized Leaflet map.

**Result:**  
The final version successfully searches live hotel data using ZIP code `16802` and displays synchronized hotel results on the list and map.

AI suggestions were reviewed and tested before being included in the final project.