<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  vehicles: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])

const handleEdit = (vehicle) => {
  emit('edit', vehicle)
}

const handleDelete = (vehicleId) => {
  emit('delete', vehicleId)
}
</script>

<template>
  <div class="vehicle-list">
    <div v-if="vehicles.length === 0" class="no-vehicles">
      No vehicles added yet.
    </div>
    <ul v-else>
      <li v-for="vehicle in vehicles" :key="vehicle.id" class="vehicle-item">
        <div class="vehicle-info">
          <strong>車號: {{ vehicle.license_plate }}</strong>
          <p>廠牌: {{ vehicle.make || 'N/A' }}</p>
          <p>車型: {{ vehicle.model || 'N/A' }}</p>
          <p>座位數: {{ vehicle.capacity || 'N/A' }}</p>
          <p>顏色: {{ vehicle.color || 'N/A' }}</p>
          <p>出廠年月: {{ vehicle.manufacture_year || 'N/A' }}</p>
          <p>保單有效日: {{ vehicle.insurance_valid_date || 'N/A' }}</p>
          <p>乘客保險金額: {{ vehicle.passenger_insurance_amount || 'N/A' }}</p>
        </div>
        <div class="vehicle-actions">
          <button @click="handleEdit(vehicle)" class="edit-btn">Edit</button>
          <button @click="handleDelete(vehicle.id)" class="delete-btn">Delete</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.vehicle-list {
  margin-top: 1.5rem;
}

.no-vehicles {
  text-align: center;
  color: #777;
  padding: 2rem;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

ul {
  list-style: none;
  padding: 0;
}

.vehicle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fdfdfd;
}

.vehicle-info strong {
  font-size: 1.1rem;
  color: #333;
}

.vehicle-info p {
  margin: 0.3rem 0;
  color: #666;
  font-size: 0.9rem;
}

.vehicle-actions button {
  background-color: #007bff;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  margin-left: 0.5rem;
}

.vehicle-actions button:hover {
  background-color: #0056b3;
}

.delete-btn {
  background-color: #dc3545;
}

.delete-btn:hover {
  background-color: #c82333;
}
</style>
