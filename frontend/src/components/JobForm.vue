<script setup>
import { ref, defineEmits, defineProps, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  initialJobData: {
    type: Object,
    default: null
  },
  isUpdate: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object, // Pass current user to get their vehicles and driver info
    default: null
  }
})

const job = ref({})
const vehicles = ref([])
const selectedVehicleId = ref(null)

const emit = defineEmits(['createJob', 'updateJob'])

const jobStatuses = ['pending', 'assigned', 'completed', 'cancelled']

// Watch initialJobData to pre-fill form when in update mode
watch(() => props.initialJobData, (newVal) => {
  if (newVal) {
    job.value = { ...newVal }
    // If updating, try to pre-select the vehicle if vehicle_number matches
    const foundVehicle = vehicles.value.find(v => v.license_plate === newVal.vehicle_number)
    if (foundVehicle) {
      selectedVehicleId.value = foundVehicle.id
    }
  } else {
    // Reset form for new job
    job.value = {
      status: 'pending',
      is_public: false
    }
    selectedVehicleId.value = null
  }
}, { immediate: true, deep: true })

// Fetch vehicles when component is mounted or currentUser changes
const fetchVehicles = async () => {
  if (!props.currentUser) return
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/vehicles/?username=${props.currentUser.username}`
    )
    vehicles.value = response.data
    console.log('Fetched vehicles in JobForm:', vehicles.value)

    // Auto-fill driver info if current user is a driver
    if (props.currentUser.roles.includes('driver') && props.currentUser.driver_profile) {
      job.value.driver_name = props.currentUser.driver_profile.chinese_name || props.currentUser.name || props.currentUser.username
      job.value.driver_phone = props.currentUser.driver_profile.phone_number
    }

  } catch (err) {
    console.error('Error fetching vehicles in JobForm:', err.response ? err.response.data : err)
    alert(`Failed to fetch vehicles: ${err.response ? err.response.data.detail : err.message}`)
  }
}

onMounted(() => {
  if (props.currentUser) {
    fetchVehicles()
  }
})
watch(() => props.currentUser, (newVal) => {
  if (newVal) {
    fetchVehicles()
  }
})

// Watch selectedVehicleId to auto-fill job fields
watch(selectedVehicleId, (newVal) => {
  const selectedVehicle = vehicles.value.find(v => v.id === newVal)
  if (selectedVehicle) {
    job.value.vehicle_number = selectedVehicle.license_plate
    job.value.vehicle_type = selectedVehicle.make // Use make as vehicle_type (廠牌)
    job.value.vehicle_model = selectedVehicle.model // Use model as vehicle_model (車型)
    job.value.num_of_passenger = selectedVehicle.capacity // Assuming capacity maps to num_of_passenger
  } else {
    // Clear vehicle related fields if no vehicle is selected
    job.value.vehicle_number = ''
    job.value.vehicle_type = ''
    job.value.vehicle_model = ''
    job.value.num_of_passenger = ''
  }
})

const handleSubmit = () => {
  if (props.isUpdate) {
    emit('updateJob', { id: props.initialJobData.id, data: job.value })
  } else {
    emit('createJob', job.value)
  }
  // Clear form after submission (only for create mode, update mode will be handled by parent)
  if (!props.isUpdate) {
    job.value = {
      status: 'pending',
      is_public: false
    }
    selectedVehicleId.value = null
  }
}
</script>

<template>
  <div class="job-form-container">
    <h3>{{ isUpdate ? 'Edit Job' : 'Create New Job' }}</h3>
    <div class="form-group">
      <label for="company">Company:</label>
      <input type="text" id="company" v-model="job.company" />
    </div>
    <div class="form-group">
      <label for="transfer_type">Transfer Type:</label>
      <input type="text" id="transfer_type" v-model="job.transfer_type" />
    </div>
    <div class="form-group">
      <label for="pick_up_date">Pick Up Date:</label>
      <input type="date" id="pick_up_date" v-model="job.pick_up_date" />
    </div>
    <div class="form-group">
      <label for="pick_up_time">Pick Up Time:</label>
      <input type="time" id="pick_up_time" v-model="job.pick_up_time" />
    </div>
    <div class="form-group">
      <label for="flight_number">Flight Number:</label>
      <input type="text" id="flight_number" v-model="job.flight_number" />
    </div>
    <div class="form-group">
      <label for="passenger_name">Passenger Name:</label>
      <input type="text" id="passenger_name" v-model="job.passenger_name" />
    </div>
    <div class="form-group">
      <label for="phone_number">Phone Number:</label>
      <input type="text" id="phone_number" v-model="job.phone_number" />
    </div>

    <div class="form-group">
      <label for="selectVehicle">Select Vehicle:</label>
      <select id="selectVehicle" v-model="selectedVehicleId">
        <option :value="null">-- Select a Vehicle --</option>
        <option v-for="v in vehicles" :key="v.id" :value="v.id">
          {{ v.license_plate }} ({{ v.make }} {{ v.model }})
        </option>
      </select>
    </div>

    <div class="form-group">
      <label for="vehicle_number">車號:</label>
      <input type="text" id="vehicle_number" v-model="job.vehicle_number" />
    </div>
    <div class="form-group">
      <label for="vehicle_model">廠牌 (Make):</label>
      <input type="text" id="vehicle_model" v-model="job.vehicle_model" />
    </div>
    <div class="form-group">
      <label for="vehicle_type">車型 (Model):</label>
      <input type="text" id="vehicle_type" v-model="job.vehicle_type" />
    </div>
    <div class="form-group">
      <label for="num_of_passenger">No. of Passenger:</label>
      <input type="text" id="num_of_passenger" v-model="job.num_of_passenger" />
    </div>

    <div class="form-group">
      <label for="from_location">From:</label>
      <input type="text" id="from_location" v-model="job.from_location" />
    </div>
    <div class="form-group">
      <label for="to_location">To:</label>
      <input type="text" id="to_location" v-model="job.to_location" />
    </div>
    <div class="form-group">
      <label for="additional_services">Additional Services:</label>
      <input type="text" id="additional_services" v-model="job.additional_services" />
    </div>
    <div class="form-group">
      <label for="special_requirements">Special Requirements:</label>
      <input type="text" id="special_requirements" v-model="job.special_requirements" />
    </div>
    <div class="form-group">
      <label for="other_contact_info">Other Contact Information:</label>
      <input type="text" id="other_contact_info" v-model="job.other_contact_info" />
    </div>
    <div class="form-group">
      <label for="order_number">Order Number:</label>
      <input type="text" id="order_number" v-model="job.order_number" />
    </div>
    <div class="form-group">
      <label for="total_price">Total Price:</label>
      <input type="text" id="total_price" v-model="job.total_price" />
    </div>
    <div class="form-group">
      <label for="email">E-mail:</label>
      <input type="text" id="email" v-model="job.email" />
    </div>
    <div class="form-group">
      <label for="driver_name">駕駛:</label>
      <input type="text" id="driver_name" v-model="job.driver_name" />
    </div>
    <div class="form-group">
      <label for="driver_phone">電話:</label>
      <input type="text" id="driver_phone" v-model="job.driver_phone" />
    </div>

    <div class="form-group checkbox-group">
      <input type="checkbox" id="isPublic" v-model="job.is_public" />
      <label for="isPublic">是否外包</label>
    </div>
    <div class="form-group">
      <label for="jobStatus">Status:</label>
      <select id="jobStatus" v-model="job.status">
        <option v-for="s in jobStatuses" :key="s" :value="s">
          {{ s.charAt(0).toUpperCase() + s.slice(1) }}
        </option>
      </select>
    </div>
    <button @click="handleSubmit">{{ isUpdate ? 'Update Job' : 'Create Job' }}</button>
  </div>
</template>

<style scoped>
.job-form-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
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
.form-group input[type="date"],
.form-group input[type="time"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.form-group.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.form-group.checkbox-group label {
  margin-bottom: 0;
}

button {
  background-color: #42b983;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  width: 100%;
}

button:hover {
  background-color: #369f75;
}
</style>
