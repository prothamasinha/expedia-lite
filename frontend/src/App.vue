<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const zipCode = ref('')
const hotels = ref([])
const center = ref(null)
const selectedHotelId = ref(null)
const status = ref('idle')
const message = ref('')

const mapElement = ref(null)

let map = null
let markers = new Map()

async function searchHotels() {
  const zip = zipCode.value.trim()

  hotels.value = []
  center.value = null
  selectedHotelId.value = null
  message.value = ''

  if (!/^\d{5}$/.test(zip)) {
    status.value = 'invalid'
    message.value = 'Please enter a valid five-digit U.S. ZIP code.'
    clearMap()
    return
  }

  status.value = 'loading'

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/hotels/nearby?zip_code=${encodeURIComponent(zip)}`
    )

    const data = await response.json()

    if (!response.ok) {
      if (response.status === 404) {
        status.value = 'unresolved'
        message.value =
          data.detail || 'That U.S. ZIP code could not be resolved.'
      } else {
        status.value = 'error'
        message.value =
          data.detail || 'The hotel search request failed.'
      }

      clearMap()
      return
    }

    center.value = data.center
    hotels.value = data.hotels || []

    if (hotels.value.length === 0) {
      status.value = 'empty'
      message.value = 'No nearby hotels were returned for this ZIP code.'
      clearMap()
      return
    }

    status.value = 'results'

    await nextTick()
    buildMap()
  } catch (error) {
    status.value = 'error'
    message.value =
      'The request could not be completed. Please try again.'
    clearMap()
  }
}

function buildMap() {
  clearMap()

  if (!center.value || !mapElement.value) {
    return
  }

  map = L.map(mapElement.value).setView(
    [
      center.value.latitude,
      center.value.longitude
    ],
    13
  )

  L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      attribution:
        '&copy; OpenStreetMap contributors'
    }
  ).addTo(map)

  L.circleMarker(
    [
      center.value.latitude,
      center.value.longitude
    ],
    {
      radius: 7
    }
  )
    .addTo(map)
    .bindPopup(`Search center: ${zipCode.value}`)

  hotels.value.forEach((hotel, index) => {
    if (
      hotel.latitude == null ||
      hotel.longitude == null
    ) {
      return
    }

    const hotelId =
      hotel.place_id || `hotel-${index}`

    const marker = L.circleMarker(
      [
        hotel.latitude,
        hotel.longitude
      ],
      {
        radius: 9
      }
    )
      .addTo(map)
      .bindPopup(
        `<strong>${escapeHtml(hotel.name)}</strong><br>${escapeHtml(
          hotel.address || 'Address unavailable'
        )}`
      )

    marker.on('click', () => {
      selectHotel(hotelId, false)
    })

    markers.set(hotelId, marker)
  })
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

onBeforeUnmount(() => {
  clearMap()
})
</script>

<template>
  <main>
    <header>
      <h1>Hotel Discovery</h1>
      <p>
        Search for hotels near the center of a U.S. ZIP code.
      </p>
    </header>

    <section class="search-card">
      <label for="zip">
        U.S. ZIP Code
      </label>

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
      >
        Searching Geoapify for nearby hotels...
      </p>

      <p
        v-if="
          status === 'invalid' ||
          status === 'unresolved' ||
          status === 'empty' ||
          status === 'error'
        "
        class="status"
      >
        {{ message }}
      </p>
    </section>

    <section
      v-if="status === 'results'"
      class="results-layout"
    >
      <div class="results-panel">
        <h2>
          Hotels near {{ zipCode }}
        </h2>

        <p class="summary">
          {{ hotels.length }} hotel result<span
            v-if="hotels.length !== 1"
          >s</span>
          returned by Geoapify.
        </p>

        <button
          v-for="(hotel, index) in hotels"
          :id="`hotel-${hotel.place_id || `hotel-${index}`}`"
          :key="hotel.place_id || index"
          type="button"
          class="hotel-card"
          :class="{
            selected:
              selectedHotelId ===
              (hotel.place_id || `hotel-${index}`)
          }"
          @click="
            selectHotel(
              hotel.place_id || `hotel-${index}`
            )
          "
        >
          <strong>
            {{ hotel.name }}
          </strong>

          <span v-if="hotel.address">
            {{ hotel.address }}
          </span>

          <span v-if="hotel.distance != null">
            Approximately
            {{ (hotel.distance / 1000).toFixed(1) }}
            km from the search center
          </span>
        </button>
      </div>

      <div class="map-panel">
        <h2>Map</h2>

        <p v-if="center">
          Search center:
          {{ center.formatted }}
        </p>

        <div
          ref="mapElement"
          class="map"
          aria-label="Map of nearby hotels"
        ></div>
      </div>
    </section>

    <footer>
      Hotel and location information comes from Geoapify.
      Results represent available provider data and do not
      indicate prices, room availability, ratings, or booking
      confirmation.
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

header p {
  margin-top: 0;
  color: #555;
}

.search-card {
  padding: 22px;
  margin-bottom: 24px;
  background: #f5f5f5;
  border-radius: 12px;
}

.search-card label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.search-row {
  display: flex;
  gap: 10px;
}

input {
  width: 220px;
  padding: 11px;
  font-size: 16px;
}

button {
  font: inherit;
}

.search-row button {
  padding: 11px 18px;
  cursor: pointer;
}

.search-row button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.status {
  margin-bottom: 0;
  margin-top: 14px;
}

.results-layout {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 24px;
}

.results-panel,
.map-panel {
  min-width: 0;
}

.summary {
  color: #555;
}

.results-panel {
  max-height: 650px;
  overflow-y: auto;
  padding-right: 5px;
}

.hotel-card {
  display: block;
  width: 100%;
  padding: 16px;
  margin-bottom: 10px;
  text-align: left;
  background: white;
  border: 1px solid #ccc;
  border-radius: 9px;
  cursor: pointer;
}

.hotel-card:hover,
.hotel-card:focus {
  border: 2px solid #555;
}

.hotel-card.selected {
  border: 3px solid #222;
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

.map {
  width: 100%;
  height: 560px;
  border-radius: 12px;
  overflow: hidden;
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
}
</style>