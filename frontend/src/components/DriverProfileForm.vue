<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ license_number: '', vehicle_type: '' })
  }
})

const licenseNumber = ref(props.initialData.license_number)
const vehicleType = ref(props.initialData.vehicle_type)

const emit = defineEmits(['update'])

watch(() => props.initialData, (newVal) => {
  licenseNumber.value = newVal.license_number
  vehicleType.value = newVal.vehicle_type
}, { deep: true, immediate: true })

const updateProfile = () => {
  emit('update', {
    license_number: licenseNumber.value,
    vehicle_type: vehicleType.value
  })
}

// Emit update whenever input changes
watch([licenseNumber, vehicleType], updateProfile)
</script>

<template>
  <div class="profile-form-section">
    <h3>Driver Profile</h3>
    <div class="form-group">
      <label for="licenseNumber">License Number:</label>
      <input type="text" id="licenseNumber" v-model="licenseNumber" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="vehicleType">Vehicle Type:</label>
      <input type="text" id="vehicleType" v-model="vehicleType" @input="updateProfile" />
    </div>
  </div>
</template>

<style scoped>
.profile-form-section {
  border: 1px solid #eee;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1.5rem;
  background-color: #f9f9f9;
}

h3 {
  color: #42b983;
  margin-top: 0;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
</style>
