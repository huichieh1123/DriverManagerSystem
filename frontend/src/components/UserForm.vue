<script setup>
import { ref, watch } from 'vue'
import DriverProfileForm from './DriverProfileForm.vue'
import DispatcherProfileForm from './DispatcherProfileForm.vue'
import CompanyProfileForm from './CompanyProfileForm.vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ username: '', name: '', roles: [], driver_profile: {}, dispatcher_profile: {}, company_profile: {} })
  },
  isUpdate: {
    type: Boolean,
    default: false
  },
  showRoleProfiles: {
    type: Boolean,
    default: true // Default to true, so it shows by default for profile editing
  }
})

const username = ref(props.initialData.username)
const password = ref('')
const name = ref(props.initialData.name)
const selectedRoles = ref(props.initialData.roles)

// Reactive state for nested profiles
const driverProfileData = ref(props.initialData.driver_profile || {})
const dispatcherProfileData = ref(props.initialData.dispatcher_profile || {})
const companyProfileData = ref(props.initialData.company_profile || {})

const emit = defineEmits(['register', 'login', 'update'])

const roles = ['driver', 'dispatcher', 'company']

const showDriverProfile = ref(false)
const showDispatcherProfile = ref(false)
const showCompanyProfile = ref(false)

// Watch for changes in initialData when props are updated (e.g., after login)
watch(() => props.initialData, (newVal) => {
  username.value = newVal.username
  name.value = newVal.name
  selectedRoles.value = newVal.roles
  driverProfileData.value = newVal.driver_profile || {}
  dispatcherProfileData.value = newVal.dispatcher_profile || {}
  companyProfileData.value = newVal.company_profile || {}
}, { deep: true, immediate: true })

const handleRegister = () => {
  emit('register', {
    username: username.value,
    password: password.value,
    name: name.value,
    roles: selectedRoles.value,
    driver_profile: driverProfileData.value,
    dispatcher_profile: dispatcherProfileData.value,
    company_profile: companyProfileData.value,
  })
}

const handleLogin = () => {
  emit('login', { username: username.value, password: password.value })
}

const handleUpdate = () => {
  const updatePayload = {
    name: name.value,
    roles: selectedRoles.value,
  }

  if (selectedRoles.value.includes('driver')) {
    updatePayload.driver_profile = driverProfileData.value
  }
  if (selectedRoles.value.includes('dispatcher')) {
    updatePayload.dispatcher_profile = dispatcherProfileData.value
  }
  if (selectedRoles.value.includes('company')) {
    updatePayload.company_profile = companyProfileData.value
  }

  emit('update', updatePayload)
}

const updateDriverProfile = (data) => {
  driverProfileData.value = { ...driverProfileData.value, ...data }
}
const updateDispatcherProfile = (data) => {
  dispatcherProfileData.value = { ...dispatcherProfileData.value, ...data }
}
const updateCompanyProfile = (data) => {
  companyProfileData.value = { ...companyProfileData.value, ...data }
}
</script>

<template>
  <div class="user-form-container">
    <h2>{{ isUpdate ? 'Update Profile' : 'User Authentication' }}</h2>
    <div class="form-group">
      <label for="username">Username:</label>
      <input type="text" id="username" v-model="username" :disabled="isUpdate" />
    </div>
    <div class="form-group" v-if="!isUpdate">
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" />
    </div>
    <div class="form-group">
      <label for="name">Name:</label>
      <input type="text" id="name" v-model="name" />
    </div>
    <div class="form-group">
      <label>Roles:</label>
      <div class="roles-checkboxes">
        <label v-for="role in roles" :key="role">
          <input type="checkbox" :value="role" v-model="selectedRoles" />
          {{ role.charAt(0).toUpperCase() + role.slice(1) }}
        </label>
      </div>
    </div>

    <!-- Dynamic Profile Forms -->
    <div v-if="showRoleProfiles && (isUpdate || selectedRoles.length > 0)">
      <div v-if="selectedRoles.includes('driver')">
        <h3 @click="showDriverProfile = !showDriverProfile">Driver Profile (click to expand)</h3>
        <DriverProfileForm
          v-if="showDriverProfile"
          :initialData="driverProfileData"
          :companyName="initialData.company_name"
          @update="updateDriverProfile"
        />
      </div>
      <div v-if="selectedRoles.includes('dispatcher')">
        <h3 @click="showDispatcherProfile = !showDispatcherProfile">Dispatcher Profile (click to expand)</h3>
        <DispatcherProfileForm
          v-if="showDispatcherProfile"
          :initialData="dispatcherProfileData"
          @update="updateDispatcherProfile"
        />
      </div>
      <div v-if="selectedRoles.includes('company')">
        <h3 @click="showCompanyProfile = !showCompanyProfile">Company Profile (click to expand)</h3>
        <CompanyProfileForm
          v-if="showCompanyProfile"
          :initialData="companyProfileData"
          @update="updateCompanyProfile"
        />
      </div>
    </div>

    <div class="form-actions">
      <button v-if="!isUpdate" @click="handleRegister">Register</button>
      <button v-if="!isUpdate" @click="handleLogin">Login</button>
      <button v-if="isUpdate" @click="handleUpdate">Update Profile</button>
    </div>
  </div>
</template>

<style scoped>
.user-form-container {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
}

h3 {
  cursor: pointer;
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
.form-group input[type="password"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.roles-checkboxes label {
  display: inline-flex;
  align-items: center;
  margin-right: 1rem;
  cursor: pointer;
}

.roles-checkboxes input[type="checkbox"] {
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 1.5rem;
}

.form-actions button {
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
</style>
