
<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const API = 'http://127.0.0.1:8000'

// --------------------------------------------------
// PART 1 - HOTEL SEARCH
// --------------------------------------------------

const zipCode = ref('')
const hotels = ref([])
const center = ref(null)
const selectedHotelId = ref(null)
const status = ref('idle')
const message = ref('')

const mapElement = ref(null)
let map = null
let markers = new Map()

// --------------------------------------------------
// PART 2 - LOCAL HOTEL STORAGE
// --------------------------------------------------

const savedHotels = ref([])
const savedStatus = ref('idle')
const localMessage = ref('')
const savingId = ref(null)
const removingId = ref(null)

const savedPlaceIds = computed(() => {
  return new Set(savedHotels.value.map(h => h.place_id))
})

// --------------------------------------------------
// PART 2 - AI CHATBOT
// --------------------------------------------------

const chatQuestion = ref('')
const chatStatus = ref('idle')
const chatResult = ref(null)
const chatError = ref('')

// --------------------------------------------------
// SHARED ERROR HANDLING
// --------------------------------------------------

async function readResponse(response) {
  let data

  try {
    data = await response.json()
  } catch {
    throw new Error('The server returned an invalid response.')
  }

  if (!response.ok) {
    const detail = data.detail

    let errorMessage = 'The request failed.'

    if (typeof detail === 'string') {
      errorMessage = detail
    } else if (detail && typeof detail === 'object') {
      errorMessage = detail.message || JSON.stringify(detail)
    }

    throw new Error(errorMessage)
  }

  return data
}

// --------------------------------------------------
// PART 1 - SEARCH GEOAPIFY HOTELS
// --------------------------------------------------

async function searchHotels() {
  const zip = zipCode.value.trim()

  clearMap()
  hotels.value = []
  center.value = null
  selectedHotelId.value = null
  message.value = ''

  if (!/^\d{5}$/.test(zip)) {
    status.value = 'invalid'
    message.value = 'Please enter a valid five-digit U.S. ZIP code.'
    return
  }

  status.value = 'loading'

  try {
    const response = await fetch(
      `${API}/hotels/nearby?zip_code=${encodeURIComponent(zip)}`
    )

    if (response.status === 404) {
      const data = await response.json()
      status.value = 'unresolved'
      message.value =
        data.detail || 'That U.S. ZIP code could not be resolved.'
      return
    }

    const data = await readResponse(response)

    center.value = data.center
    hotels.value = data.hotels || []

    if (hotels.value.length === 0) {
      status.value = 'empty'
      message.value = 'No nearby hotels were returned for this ZIP code.'
      return
    }

    status.value = 'results'

    await nextTick()
    buildMap()

  } catch (error) {
    status.value = 'error'
    message.value = error.message || 'Hotel search failed.'
    clearMap()
  }
}

// --------------------------------------------------
// PART 1 - LEAFLET MAP
// --------------------------------------------------

function buildMap() {
  clearMap()

  if (!center.value || !mapElement.value) {
    return
  }

  map = L.map(mapElement.value).setView(
    [center.value.latitude, center.value.longitude],
    13
  )

  L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      attribution: '&copy; OpenStreetMap contributors'
    }
  ).addTo(map)

  L.circleMarker(
    [center.value.latitude, center.value.longitude],
    { radius: 7 }
  )
    .addTo(map)
    .bindPopup(`Search center: ${escapeHtml(zipCode.value)}`)

  hotels.value.forEach((hotel, index) => {
    if (
      hotel.latitude == null ||
      hotel.longitude == null
    ) {
      return
    }

    const hotelId = hotel.place_id || `hotel-${index}`

    const marker = L.circleMarker(
      [hotel.latitude, hotel.longitude],
      { radius: 9 }
    )
      .addTo(map)
      .bindPopup(
        `<strong>${escapeHtml(hotel.name)}</strong><br>` +
        escapeHtml(hotel.address || 'Address unavailable')
      )

    marker.on('click', () => {
      selectHotel(hotelId, false)
    })

    markers.set(hotelId, marker)
  })

  setTimeout(() => {
    if (map) map.invalidateSize()
  }, 100)
}

function selectHotel(hotelId, openMarker = true) {
  selectedHotelId.value = hotelId

  if (openMarker) {
    const marker = markers.get(hotelId)

    if (marker && map) {
      map.setView(marker.getLatLng(), 15)
      marker.openPopup()
    }
  }

  nextTick(() => {
    const element = document.getElementById(
      `hotel-${hotelId}`
    )

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      })
    }
  })
}

function clearMap() {
  markers.clear()

  if (map) {
    map.remove()
    map = null
  }
}

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

// --------------------------------------------------
// PART 2 - LOAD SAVED HOTELS
// --------------------------------------------------

async function loadSavedHotels() {
  savedStatus.value = 'loading'

  try {
    const response = await fetch(`${API}/local/hotels`)
    const data = await readResponse(response)

    savedHotels.value = data.hotels || []
    savedStatus.value = 'ready'

  } catch (error) {
    savedStatus.value = 'error'
    localMessage.value =
      'Could not load saved hotels: ' + error.message
  }
}

// --------------------------------------------------
// PART 2 - SAVE A GEOAPIFY HOTEL
// --------------------------------------------------

async function saveHotel(hotel) {
  if (!hotel.place_id) {
    localMessage.value =
      'This hotel has no provider identifier and cannot be saved.'
    return
  }

  savingId.value = hotel.place_id
  localMessage.value = ''

  try {
    const response = await fetch(`${API}/local/hotels`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        place_id: hotel.place_id,
        name: hotel.name,
        address: hotel.address,
        city: hotel.city,
        state: hotel.state,
        postcode: hotel.postcode,
        latitude: hotel.latitude,
        longitude: hotel.longitude,
        search_zip: zipCode.value.trim()
      })
    })

    const data = await readResponse(response)

    await loadSavedHotels()

    localMessage.value = data.newly_saved
      ? `${hotel.name} was saved locally. Simulated nightly data was added.`
      : `${hotel.name} is already saved locally.`

  } catch (error) {
    localMessage.value =
      'Could not save hotel: ' + error.message

  } finally {
    savingId.value = null
  }
}

// --------------------------------------------------
// PART 2 - REMOVE SAVED HOTEL
// --------------------------------------------------

async function removeHotel(hotel) {
  removingId.value = hotel.place_id
  localMessage.value = ''

  try {
    const response = await fetch(
      `${API}/local/hotels/${encodeURIComponent(hotel.place_id)}`,
      { method: 'DELETE' }
    )

    await readResponse(response)
    await loadSavedHotels()

    localMessage.value = `${hotel.hotel_name} was removed from local storage.`

  } catch (error) {
    localMessage.value =
      'Could not remove hotel: ' + error.message

  } finally {
    removingId.value = null
  }
}

// --------------------------------------------------
// PART 2 - RAG AI CHATBOT
// --------------------------------------------------

async function askChatbot() {
  const question = chatQuestion.value.trim()

  if (question.length < 3) {
    chatStatus.value = 'error'
    chatError.value = 'Please enter a hotel question.'
    return
  }

  chatStatus.value = 'loading'
  chatResult.value = null
  chatError.value = ''

  try {
    const response = await fetch(`${API}/chat/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question
      })
    })

    const data = await readResponse(response)

    chatResult.value = data
    chatStatus.value =
      data.row_count === 0 ? 'no-match' : 'answer'

  } catch (error) {
    chatStatus.value = 'error'
    chatError.value = error.message ||
      'The chatbot could not answer this question.'
  }
}

// --------------------------------------------------
// INITIALIZATION AND CLEANUP
// --------------------------------------------------

onMounted(() => {
  loadSavedHotels()
})

onBeforeUnmount(() => {
  clearMap()
})
</script>

<template>
  <main>
    <header>
      <h1>Hotel Discovery</h1>

      <p>
        Explore nearby hotels, save favorites, and compare
        simulated nightly rates with an AI assistant.
      </p>
    </header>

    <!-- PART 1 - ZIP SEARCH -->

    <section class="search-card">
      <h2>Find Hotels</h2>

      <label for="zip">U.S. ZIP Code</label>

      <div class="search-row">
        <input
          id="zip"
          v-model="zipCode"
          maxlength="5"
          inputmode="numeric"
          placeholder="Example: 16802"
          @keyup.enter="searchHotels"
        />

        <button
          type="button"
          @click="searchHotels"
          :disabled="status === 'loading'"
        >
          {{
            status === 'loading'
              ? 'Searching...'
              : 'Search Hotels'
          }}
        </button>
      </div>

      <p
        v-if="status === 'loading'"
        class="status"
        role="status"
      >
        Searching Geoapify for nearby hotels...
      </p>

      <p
        v-if="['invalid', 'unresolved', 'empty', 'error'].includes(status)"
        class="status error"
        role="alert"
      >
        {{ message }}
      </p>
    </section>

    <!-- PART 1 - HOTEL RESULTS AND MAP -->

    <section
      v-if="status === 'results'"
      class="results-layout"
    >
      <div class="results-panel">
        <h2>Hotels near {{ zipCode }}</h2>

        <p class="summary">
          {{ hotels.length }} hotel result(s) returned by Geoapify.
        </p>

        <div
          v-for="(hotel, index) in hotels"
          :id="`hotel-${hotel.place_id || `hotel-${index}`}`"
          :key="hotel.place_id || index"
          class="hotel-item"
        >
          <button
            type="button"
            class="hotel-card"
            :class="{
              selected:
                selectedHotelId ===
                (hotel.place_id || `hotel-${index}`)
            }"
            :aria-pressed="
              selectedHotelId ===
              (hotel.place_id || `hotel-${index}`)
            "
            @click="
              selectHotel(hotel.place_id || `hotel-${index}`)
            "
          >
            <strong>{{ hotel.name }}</strong>

            <span v-if="hotel.address">
              {{ hotel.address }}
            </span>

            <span v-if="hotel.distance != null">
              Approximately
              {{ (hotel.distance / 1000).toFixed(1) }}
              km from the search center
            </span>
          </button>

          <button
            type="button"
            class="save-button"
            :disabled="
              !hotel.place_id ||
              savedPlaceIds.has(hotel.place_id) ||
              savingId === hotel.place_id
            "
            @click="saveHotel(hotel)"
          >
            {{
              savedPlaceIds.has(hotel.place_id)
                ? 'Saved Locally'
                : savingId === hotel.place_id
                  ? 'Saving...'
                  : 'Add to Local'
            }}
          </button>
        </div>
      </div>

      <div class="map-panel">
        <h2>Map</h2>

        <p v-if="center">
          Search center: {{ center.formatted }}
        </p>

        <div
          ref="mapElement"
          class="map"
          aria-label="Map of nearby hotels"
        ></div>
      </div>
    </section>

    <!-- PART 2 - LOCAL HOTEL SHORTLIST -->

    <section class="saved-section">
      <div class="section-heading">
        <h2>Saved Hotels</h2>

        <button
          type="button"
          class="secondary-button"
          @click="loadSavedHotels"
          :disabled="savedStatus === 'loading'"
        >
          Refresh
        </button>
      </div>

      <p class="helper">
        Hotels saved in your local SQLite database.
        These records remain available after restarting the application.
      </p>

      <p v-if="savedStatus === 'loading'" role="status">
        Loading saved hotels...
      </p>

      <p
        v-if="localMessage"
        class="local-message"
        role="status"
      >
        {{ localMessage }}
      </p>

      <p
        v-if="savedStatus === 'ready' && savedHotels.length === 0"
      >
        No saved hotels yet. Search for hotels and select Add to Local.
      </p>

      <div
        v-for="hotel in savedHotels"
        :key="hotel.place_id"
        class="saved-hotel"
      >
        <div>
          <h3>{{ hotel.hotel_name }}</h3>

          <p>{{ hotel.address || 'Address unavailable' }}</p>

          <p v-if="hotel.search_zip">
            Saved from ZIP {{ hotel.search_zip }}
          </p>
        </div>

        <button
          type="button"
          class="remove-button"
          @click="removeHotel(hotel)"
          :disabled="removingId === hotel.place_id"
        >
          {{
            removingId === hotel.place_id
              ? 'Removing...'
              : 'Remove from Local'
          }}
        </button>
      </div>
    </section>

    <!-- PART 2 - RAG CHATBOT -->

    <section class="chat-section">
      <h2>AI Hotel Assistant</h2>

      <p class="helper">
        Ask questions about locally saved hotels, simulated
        nightly rates, room availability, and stay costs.
      </p>

      <p class="disclaimer">
        Course demonstration only. Prices and availability
        are simulated and do not represent real bookings.
      </p>

      <form @submit.prevent="askChatbot">
        <label for="chat-question">
          Your hotel question
        </label>

        <textarea
          id="chat-question"
          v-model="chatQuestion"
          rows="3"
          placeholder="Example: What is the simulated nightly rate for a saved hotel on October 9, 2026?"
        ></textarea>

        <button
          type="submit"
          class="ask-button"
          :disabled="chatStatus === 'loading'"
        >
          {{
            chatStatus === 'loading'
              ? 'AI is thinking...'
              : 'Ask AI'
          }}
        </button>
      </form>

      <p
        v-if="chatStatus === 'loading'"
        class="chat-loading"
        role="status"
      >
        Generating SQL, checking saved records,
        and preparing an answer...
      </p>

      <p
        v-if="chatStatus === 'error'"
        class="status error"
        role="alert"
      >
        {{ chatError }}
      </p>

      <div
        v-if="chatResult"
        class="chat-answer"
        role="status"
        aria-live="polite"
      >
        <h3>AI Answer</h3>

        <p v-if="chatStatus === 'no-match'" class="no-match">
          No matching local records were retrieved.
        </p>

        <p class="answer-text">
          {{ chatResult.answer }}
        </p>

        <p class="helper">
          Retrieved {{ chatResult.row_count }} record(s)
          from the local SQLite database.
        </p>

        <p class="disclaimer">
          {{ chatResult.notice }}
        </p>

        <details class="trace-panel">
          <summary>
            View SQL and retrieved records
          </summary>

          <h4>AI-generated SQL</h4>
          <pre>{{ chatResult.proposed_sql }}</pre>

          <h4>Retrieved SQLite records</h4>
          <pre>{{ JSON.stringify(chatResult.retrieved_records, null, 2) }}</pre>

          <h4>LLM Model</h4>
          <p>{{ chatResult.model }}</p>
        </details>
      </div>
    </section>

    <footer>
      Hotel locations come from Geoapify. Geoapify does not
      provide verified room prices or availability here.
      Saved hotel prices and room availability are simulated
      for IST 402 coursework. No real bookings are performed.
    </footer>
  </main>
</template>

<style scoped>
main {
  max-width: 1250px;
  margin: 0 auto;
  padding: 32px 20px;
  font-family: Arial, sans-serif;
  color: #222;
}

header {
  margin-bottom: 28px;
}

h1 {
  margin-bottom: 6px;
  font-size: 38px;
}

header p,
.helper,
.summary {
  color: #555;
  line-height: 1.5;
}

h2 {
  margin-top: 0;
}

.search-card,
.saved-section,
.chat-section {
  padding: 24px;
  margin-bottom: 25px;
  background: #f5f5f5;
  border-radius: 12px;
}

label {
  display: block;
  margin-bottom: 9px;
  font-weight: bold;
}

.search-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

input,
textarea {
  padding: 11px;
  font-size: 16px;
  border: 1px solid #aaa;
  border-radius: 6px;
  font-family: inherit;
}

input {
  width: 220px;
  max-width: 100%;
}

textarea {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  margin-bottom: 12px;
}

button {
  font: inherit;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.search-row button,
.ask-button,
.save-button {
  padding: 11px 18px;
  background: #2458a6;
  color: white;
  border: none;
  border-radius: 6px;
}

.search-row button:hover,
.ask-button:hover,
.save-button:hover {
  background: #183e78;
}

.status,
.local-message {
  margin-top: 14px;
  line-height: 1.5;
}

.error {
  color: #a21d1d;
}

.results-layout {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 24px;
  margin-bottom: 28px;
}

.results-panel,
.map-panel {
  min-width: 0;
}

.results-panel {
  max-height: 650px;
  overflow-y: auto;
  padding-right: 5px;
}

.hotel-item {
  padding: 14px;
  margin-bottom: 12px;
  border: 1px solid #ccc;
  border-radius: 9px;
  background: white;
}

.hotel-card {
  display: block;
  width: 100%;
  padding: 6px 4px 12px;
  text-align: left;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 6px;
}

.hotel-card:hover,
.hotel-card:focus-visible {
  border-color: #555;
}

.hotel-card.selected {
  border-color: #222;
}

.hotel-card strong,
.hotel-card span {
  display: block;
}

.hotel-card strong {
  margin-bottom: 7px;
  font-size: 17px;
}

.hotel-card span {
  margin-top: 5px;
  color: #555;
  line-height: 1.4;
}

.save-button {
  margin-top: 4px;
  font-size: 14px;
}

.map {
  width: 100%;
  height: 560px;
  border-radius: 12px;
  overflow: hidden;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.secondary-button,
.remove-button {
  padding: 9px 12px;
  background: white;
  border: 1px solid #aaa;
  border-radius: 6px;
}

.remove-button {
  color: #a21d1d;
  border-color: #c66;
}

.saved-hotel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: white;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 12px;
}

.saved-hotel h3 {
  margin: 0 0 7px;
}

.saved-hotel p {
  margin: 4px 0;
  color: #555;
  line-height: 1.5;
}

.chat-section {
  background: #eef3fb;
}

.disclaimer {
  color: #805200;
  font-size: 14px;
  line-height: 1.5;
}

.chat-loading {
  color: #2458a6;
}

.chat-answer {
  margin-top: 18px;
  padding: 20px;
  border: 1px solid #c5d6ef;
  border-radius: 9px;
  background: white;
}

.chat-answer h3 {
  margin-top: 0;
}

.answer-text {
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.no-match {
  color: #855200;
  font-weight: bold;
}

.trace-panel {
  margin-top: 16px;
  padding: 12px;
  border-top: 1px solid #ddd;
}

.trace-panel summary {
  cursor: pointer;
  font-weight: bold;
}

pre {
  background: #f1f1f1;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-size: 13px;
}

footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 850px) {
  .results-layout {
    grid-template-columns: 1fr;
  }

  .map {
    height: 420px;
  }

  .saved-hotel {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
