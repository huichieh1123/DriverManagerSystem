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

const emit = defineEmits(['login-success'])

const emitLoginSuccess = (user) => {
  emit('login-success', user)
}

const handleRegister = async (userData) => {
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/v1/users/register`, userData)
    alert('Registration successful!')
    emitLoginSuccess(response.data)
  } catch (err) {
    console.error('Registration error:', err.response ? err.response.data : err)
    alert(`Registration failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}


const handleLogin = async (userData) => {
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/v1/users/login`, userData)
    alert('Login successful!')
    emitLoginSuccess(response.data) // Direct navigation
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
