<template>
  <div>
    <h1>Login / Register</h1>
    <UserForm @register="handleRegister" @login="handleLogin" :showRoleProfiles="false" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import UserForm from '../components/UserForm.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToDashboard = (user) => {
  // Store user ID as string
  localStorage.setItem('currentUser', JSON.stringify({ ...user, id: String(user.id) }))
  localStorage.setItem('currentUsername', user.username)

  if (user.roles.includes('company')) {
    router.push('/company')
  } else if (user.roles.includes('dispatcher')) {
    router.push('/dispatcher')
  } else if (user.roles.includes('driver')) {
    router.push('/driver')
  } else {
    router.push('/profile') // Default for users with no specific role page
  }
}

const handleRegister = async (userData) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/users/register', userData)
    alert('Registration successful!')
    navigateToDashboard(response.data) // Direct navigation
  } catch (err) {
    console.error('Registration error:', err.response ? err.response.data : err)
    alert(`Registration failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleLogin = async (userData) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/users/login', userData)
    alert('Login successful!')
    navigateToDashboard(response.data) // Direct navigation
  } catch (err) {
    console.error('Login error:', err.response ? err.response.data : err)
    alert(`Login failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
</style>