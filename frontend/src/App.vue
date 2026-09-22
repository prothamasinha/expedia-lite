<script setup>
import { ref, onMounted } from 'vue'

const hotelName = ref('')
const results = ref([])
const users = ref([])
const bookings = ref([])
const selectedUser = ref('')
const message = ref('')

async function searchHotels() {
  const response = await fetch(
    `http://127.0.0.1:8000/search?name=${encodeURIComponent(hotelName.value)}`
  )
  results.value = await response.json()
}

async function loadUsers() {
  const response = await fetch('http://127.0.0.1:8000/users')
  users.value = await response.json()

  if (users.value.length > 0 && !selectedUser.value) {
    selectedUser.value = users.value[0].user_id
  }
}

async function loadBookings() {
  const response = await fetch('http://127.0.0.1:8000/bookings')
  bookings.value = await response.json()
}

async function createBooking(tripId) {
  if (!selectedUser.value) return

  await fetch('http://127.0.0.1:8000/bookings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: selectedUser.value,
      trip_id: tripId
    })
  })

  message.value = 'Booking created successfully.'
  await loadBookings()
}

async function cancelBooking(bookingId) {
  await fetch(`http://127.0.0.1:8000/bookings/${bookingId}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      status: 'cancelled'
    })
  })

  message.value = 'Booking cancelled.'
  await loadBookings()
}

async function deleteBooking(bookingId) {
  await fetch(`http://127.0.0.1:8000/bookings/${bookingId}`, {
    method: 'DELETE'
  })

  message.value = 'Booking deleted.'
  await loadBookings()
}

onMounted(async () => {
  await loadUsers()
  await loadBookings()
})
</script>

<template>
  <main>
    <header>
      <h1>Expedia Lite</h1>
      <p>Search hotels, create bookings, and manage your booking history.</p>
    </header>

    <section class="card">
      <h2>Find a hotel</h2>

      <div class="row">
        <input
          v-model="hotelName"
          placeholder="Enter hotel name"
        />

        <button @click="searchHotels">
          Search
        </button>
      </div>

      <div class="row">
        <label>Traveler:</label>

        <select v-model="selectedUser">
          <option
            v-for="user in users"
            :key="user.user_id"
            :value="user.user_id"
          >
            {{ user.display_name }}
          </option>
        </select>
      </div>

      <p v-if="results.length === 0 && hotelName">
        No matching hotels found.
      </p>

      <div
        v-for="result in results"
        :key="result.hotel.hotel_id"
        class="hotel"
      >
        <h3>{{ result.hotel.hotel_name }}</h3>

        <p>
          {{ result.hotel.city }}, {{ result.hotel.state }}
          · ${{ result.hotel.nightly_rate_usd }}/night
        </p>

        <table>
          <thead>
            <tr>
              <th>Trip</th>
              <th>Check In</th>
              <th>Check Out</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="trip in result.trips"
              :key="trip.trip_id"
            >
              <td>{{ trip.trip_name }}</td>
              <td>{{ trip.check_in }}</td>
              <td>{{ trip.check_out }}</td>
              <td>
                <button @click="createBooking(trip.trip_id)">
                  Book
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <p v-if="message" class="message">
      {{ message }}
    </p>

    <section class="card">
      <h2>Booking History</h2>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Traveler</th>
            <th>Hotel</th>
            <th>Trip</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="booking in bookings"
            :key="booking.booking_id"
          >
            <td>{{ booking.booking_id }}</td>
            <td>{{ booking.display_name }}</td>
            <td>{{ booking.hotel_name }}</td>
            <td>{{ booking.trip_name }}</td>
            <td>{{ booking.status }}</td>
            <td>
              <button
                v-if="booking.status !== 'cancelled'"
                @click="cancelBooking(booking.booking_id)"
              >
                Cancel
              </button>

              <button
                class="delete"
                @click="deleteBooking(booking.booking_id)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>

<style scoped>
main {
  max-width: 1100px;
  margin: 40px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

header {
  margin-bottom: 30px;
}

h1 {
  font-size: 38px;
  margin-bottom: 8px;
}

.card {
  background: #ffffff;
  color: #222222;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  align-items: center;
}

input,
select {
  padding: 10px;
  font-size: 16px;
}

input {
  width: 320px;
}

button {
  padding: 9px 14px;
  cursor: pointer;
  margin-right: 6px;
}

.delete {
  background: #b42318;
  color: white;
}

.hotel {
  margin-top: 25px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th,
td {
  border: 1px solid #cccccc;
  padding: 10px;
  text-align: left;
}

.message {
  padding: 12px;
  background: #dff7e5;
  color: #124d24;
  border-radius: 8px;
}
</style>