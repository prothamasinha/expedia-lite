<script setup>
import { ref } from 'vue'

const hotelName = ref('')
const results = ref([])
const searched = ref(false)

async function searchHotels() {
  searched.value = true

  const response = await fetch(
    `http://127.0.0.1:8000/search?name=${encodeURIComponent(hotelName.value)}`
  )

  results.value = await response.json()
}
</script>

<template>
  <main>
    <h1>Expedia Lite</h1>

    <div class="search-box">
      <input
        v-model="hotelName"
        type="text"
        placeholder="Enter hotel name"
      />

      <button @click="searchHotels">
        Search
      </button>
    </div>

    <p v-if="searched && results.length === 0">
      No matching hotels found.
    </p>

    <div
      v-for="result in results"
      :key="result.hotel.hotel_id"
      class="hotel"
    >
      <h2>{{ result.hotel.hotel_name }}</h2>

      <p>
        {{ result.hotel.city }}, {{ result.hotel.state }}
      </p>

      <p>
        Nightly Rate: ${{ result.hotel.nightly_rate_usd }}
      </p>

      <table>
        <thead>
          <tr>
            <th>Trip</th>
            <th>Check In</th>
            <th>Check Out</th>
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
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<style scoped>
main {
  max-width: 900px;
  margin: 50px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  margin-bottom: 25px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

input {
  width: 300px;
  padding: 10px;
  font-size: 16px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

.hotel {
  margin-top: 30px;
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

th {
  font-weight: bold;
}
</style>