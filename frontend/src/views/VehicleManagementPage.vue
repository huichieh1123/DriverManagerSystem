<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import VehicleForm from '../components/VehicleForm.vue'
import VehicleList from '../components/VehicleList.vue'

const props = defineProps({
  currentUser: Object
})

const vehicles = ref([])
const editingVehicle = ref(null)

const fetchVehicles = async () => {
  if (!props.currentUser) return
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/vehicles/?username=${props.currentUser.username}`
    )
    vehicles.value = response.data
  } catch (err) {
    console.error('Error fetching vehicles:', err.response ? err.response.data : err)
    alert(`Failed to fetch vehicles: ${err.response ? err.response.data.detail : err.message}`)
  }
}

onMounted(fetchVehicles)
watch(() => props.currentUser, fetchVehicles) // Re-fetch when currentUser changes

const handleCreateVehicle = async (vehicleData) => {
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/vehicles/?username=${props.currentUser.username}`,
      vehicleData
    )
    alert('Vehicle created successfully!')
    fetchVehicles() // Refresh list
    cancelEditingVehicle() // Clear form after successful creation
  } catch (err) {
    console.error('Error creating vehicle:', err.response ? err.response.data : err)
    alert(`Failed to create vehicle: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleUpdateVehicle = async ({ id, data }) => {
  try {
    await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/vehicles/${id}?username=${props.currentUser.username}`,
      data
    )
    alert('Vehicle updated successfully!')
    editingVehicle.value = null // Exit edit mode
    fetchVehicles() // Refresh list
  } catch (err) {
    console.error('Error updating vehicle:', err.response ? err.response.data : err)
    alert(`Failed to update vehicle: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleDeleteVehicle = async (vehicleId) => {
  if (confirm('Are you sure you want to delete this vehicle?')) {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/vehicles/${vehicleId}?username=${props.currentUser.username}`
      )
      alert('Vehicle deleted successfully!')
      fetchVehicles() // Refresh list
    } catch (err) {
      console.error('Error deleting vehicle:', err.response ? err.response.data : err)
      alert(`Failed to delete vehicle: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const startEditingVehicle = (vehicle) => {
  editingVehicle.value = { ...vehicle }
}

const cancelEditingVehicle = () => {
  editingVehicle.value = null
}
</script>

<template>
  <div class="vehicle-management-container">
    <h1>Vehicle Management</h1>

    <div class="form-section">
      <h2>{{ editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle' }}</h2>
      <VehicleForm
        :initialData="editingVehicle"
        :isUpdate="!!editingVehicle"
        @submit="editingVehicle ? handleUpdateVehicle($event) : handleCreateVehicle($event)"
        @cancel="cancelEditingVehicle"
      />
    </div>

    <div class="list-section">
      <h2>Your Vehicles</h2>
      <VehicleList :vehicles="vehicles" @edit="startEditingVehicle" @delete="handleDeleteVehicle" />
    </div>
  </div>
</template>

<style scoped>
.vehicle-management-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.form-section,
.list-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.form-section h2,
.list-section h2 {
  color: #007bff;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
}
</style>
