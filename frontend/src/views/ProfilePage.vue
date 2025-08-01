<template>
  <div>
    <h1>Your Profile</h1>
    <div v-if="userProfile">
      <p><strong>Username:</strong> {{ userProfile.username }}</p>
      <p><strong>Name:</strong> {{ userProfile.name || 'Not set' }}</p>
      <p><strong>Roles:</strong>
        <span v-if="userProfile.roles.length > 0">
          <span v-for="(role, index) in userProfile.roles" :key="role">
            {{ role.charAt(0).toUpperCase() + role.slice(1) }}
            <span v-if="index < userProfile.roles.length - 1">, </span>
          </span>
        </span>
        <span v-else>No roles assigned.</span>
      </p>
      <p v-if="isDispatcher && userProfile.company_name">
        <strong>Associated Company:</strong> {{ userProfile.company_name }}
      </p>
      <p v-if="isDispatcher && userProfile.dispatcher_association_status">
        <strong>Association Status:</strong> {{ userProfile.dispatcher_association_status.charAt(0).toUpperCase() + userProfile.dispatcher_association_status.slice(1) }}
      </p>

      <h2>Edit Your Profile</h2>
      <UserForm
        :initialData="userProfile"
        :isUpdate="true"
        :showRoleProfiles="true"
        @update="handleUpdateProfile"
      />
    </div>
    <div v-else>
      <p>Loading profile...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import UserForm from '../components/UserForm.vue'

const props = defineProps({
  currentUser: Object
})

const emit = defineEmits(['update:currentUser'])

const userProfile = ref(null)

const isDispatcher = computed(() => userProfile.value && userProfile.value.roles.includes('dispatcher'))

const fetchUserProfile = async () => {
  const username = localStorage.getItem('currentUsername')
  if (username) {
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/v1/users/me?username=${username}`)
      userProfile.value = response.data
    } catch (err) {
      console.error('Error fetching user profile:', err)
      userProfile.value = null
    }
  }
}

onMounted(fetchUserProfile)
watch(() => props.currentUser, fetchUserProfile) // Re-fetch if currentUser prop changes

const handleUpdateProfile = async (updatedData) => {
  if (!userProfile.value) return
  try {
    const response = await axios.put(
      `$ {import.meta.env.VITE_API_URL}/api/v1/users/me?username=${userProfile.value.username}`,
      updatedData
    )
    userProfile.value = response.data // Update local userProfile
    emit('update:currentUser', response.data) // Notify App.vue to update its currentUser
    localStorage.setItem('currentUser', JSON.stringify(response.data)) // Update localStorage
    alert('Profile updated successfully!')
  } catch (err) {
    console.error('Profile update error:', err.response ? err.response.data : err)
    alert(`Profile update failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
</style>
