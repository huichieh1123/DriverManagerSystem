<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  job: {
    type: Object,
    required: true
  },
  drivers: {
    type: Array,
    required: true
  },
  show: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['assign', 'close'])

const selectedDriverId = ref(null)
const selectedVehicleId = ref(null) // New: to store selected vehicle ID
const currentDriverVehicles = ref([]) // New: to store vehicles of the currently selected driver

// Watch for changes in props.show to reset selected values when modal opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    selectedDriverId.value = props.job.assigned_driver_id || null
    selectedVehicleId.value = null // Reset vehicle selection
  }
})

// Watch for changes in props.job to reset selected values when job changes
watch(() => props.job, (newVal) => {
  selectedDriverId.value = newVal.assigned_driver_id || null
  selectedVehicleId.value = null // Reset vehicle selection
})

// Watch for changes in selectedDriverId to update currentDriverVehicles
watch(selectedDriverId, (newDriverId) => {
  selectedVehicleId.value = null; // Reset vehicle when driver changes
  if (newDriverId) {
    const driver = props.drivers.find(d => d.id === newDriverId);
    if (driver && driver.driver_profile && driver.driver_profile.vehicles) {
      currentDriverVehicles.value = driver.driver_profile.vehicles;
    } else {
      currentDriverVehicles.value = [];
    }
  } else {
    currentDriverVehicles.value = [];
  }
}, { immediate: true }); // Run immediately to populate vehicles if a driver is pre-selected

const handleAssign = () => {
  if (!selectedDriverId.value) {
    alert('Please select a driver.')
    return
  }
  if (!selectedVehicleId.value) {
    alert('Please select a vehicle for the driver.')
    return
  }
  emit('assign', { jobId: props.job.id, driverId: selectedDriverId.value, vehicleId: selectedVehicleId.value })
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h3>Assign Job: {{ job.title }}</h3>
      <div class="form-group">
        <label for="driverSelect">Select Driver:</label>
        <select id="driverSelect" v-model="selectedDriverId">
          <option :value="null">-- Select a Driver --</option>
          <option v-for="driver in drivers" :key="driver.id" :value="driver.id">
            {{ driver.name || driver.username }}
          </option>
        </select>
      </div>

      <div class="form-group" v-if="selectedDriverId">
        <label for="vehicleSelect">Select Vehicle:</label>
        <select id="vehicleSelect" v-model="selectedVehicleId">
          <option :value="null">-- Select a Vehicle --</option>
          <option v-for="vehicle in currentDriverVehicles" :key="vehicle.id" :value="vehicle.id">
            {{ vehicle.license_plate }} ({{ vehicle.make }} {{ vehicle.model }})
          </option>
        </select>
        <p v-if="currentDriverVehicles.length === 0" class="no-vehicles-message">No vehicles found for this driver.</p>
      </div>

      <div class="modal-actions">
        <button @click="handleAssign" class="assign-btn" :disabled="!selectedDriverId || !selectedVehicleId">Assign</button>
        <button @click="handleClose" class="cancel-btn">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
}

h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.no-vehicles-message {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-actions button {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.assign-btn {
  background-color: #42b983;
  color: white;
}

.assign-btn:hover {
  background-color: #369f75;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}
</style>