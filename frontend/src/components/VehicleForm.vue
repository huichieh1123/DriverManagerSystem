<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: null
  },
  isUpdate: {
    type: Boolean,
    default: false
  }
})

const vehicle = ref({
  license_plate: '',
  make: '',
  model: '',
  capacity: null,
  color: '',
  manufacture_year: '',
  insurance_valid_date: '',
  passenger_insurance_amount: null,
})

const emit = defineEmits(['submit', 'cancel'])

watch(() => props.initialData, (newVal) => {
  if (newVal) {
    vehicle.value = { ...newVal }
  } else {
    // Reset form for new vehicle
    vehicle.value = {
      license_plate: '',
      make: '',
      model: '',
      capacity: null,
      color: '',
      manufacture_year: '',
      insurance_valid_date: '',
      passenger_insurance_amount: null,
    }
  }
}, { deep: true, immediate: true })

const handleSubmit = () => {
  if (!vehicle.value.license_plate) {
    alert('License Plate is required.')
    return
  }
  emit('submit', vehicle.value)
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="vehicle-form">
    <div class="form-group">
      <label for="license_plate">車號:</label>
      <input type="text" id="license_plate" v-model="vehicle.license_plate" />
    </div>
    <div class="form-group">
      <label for="make">廠牌:</label>
      <input type="text" id="make" v-model="vehicle.make" />
    </div>
    <div class="form-group">
      <label for="model">車型:</label>
      <input type="text" id="model" v-model="vehicle.model" />
    </div>
    <div class="form-group">
      <label for="capacity">座位數:</label>
      <input type="number" id="capacity" v-model="vehicle.capacity" />
    </div>
    <div class="form-group">
      <label for="color">顏色:</label>
      <input type="text" id="color" v-model="vehicle.color" />
    </div>
    <div class="form-group">
      <label for="manufacture_year">出廠年月:</label>
      <input type="month" id="manufacture_year" v-model="vehicle.manufacture_year" />
    </div>
    <div class="form-group">
      <label for="insurance_valid_date">保單有效日:</label>
      <input type="date" id="insurance_valid_date" v-model="vehicle.insurance_valid_date" />
    </div>
    <div class="form-group">
      <label for="passenger_insurance_amount">乘客保險金額:</label>
      <input type="number" id="passenger_insurance_amount" v-model="vehicle.passenger_insurance_amount" />
    </div>
    <div class="form-actions">
      <button @click="handleSubmit">{{ isUpdate ? 'Update Vehicle' : 'Add Vehicle' }}</button>
      <button v-if="isUpdate" @click="handleCancel" class="cancel-btn">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.vehicle-form {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #fdfdfd;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="month"],
.form-group input[type="date"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.form-actions button {
  flex: 1;
  background-color: #42b983;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.form-actions button:hover {
  background-color: #369f75;
}

.cancel-btn {
  background-color: #6c757d;
}

.cancel-btn:hover {
  background-color: #5a6268;
}
</style>
