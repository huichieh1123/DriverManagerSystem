<script setup>
import { computed, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const currentUser = ref(JSON.parse(localStorage.getItem('currentUser')))

const isLoggedIn = computed(() => !!currentUser.value)
const isCompany = computed(() => currentUser.value && currentUser.value.roles.includes('company'))
const isDispatcher = computed(() => currentUser.value && currentUser.value.roles.includes('dispatcher'))
const isDriver = computed(() => currentUser.value && currentUser.value.roles.includes('driver'))

// Function to fetch current user's data
const fetchCurrentUser = async () => {
  const username = localStorage.getItem('currentUsername');
  if (username) {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/v1/users/me?username=${username}`);
      currentUser.value = response.data;
      localStorage.setItem('currentUser', JSON.stringify(response.data)); // Ensure localStorage is updated with latest data
    } catch (err) {
      console.error('Error fetching current user:', err);
      currentUser.value = null; // Clear user if fetch fails
      localStorage.removeItem('currentUser');
      localStorage.removeItem('currentUsername');
    }
  }
};

// Watch for changes in localStorage's currentUser (e.g., from LoginPage)
watch(() => localStorage.getItem('currentUser'), (newVal) => {
  currentUser.value = newVal ? JSON.parse(newVal) : null
  if (currentUser.value) {
    // Redirect to appropriate page after login
    if (isCompany.value) {
      router.push('/company')
    } else if (isDispatcher.value) {
      router.push('/dispatcher')
    } else if (isDriver.value) {
      router.push('/driver')
    } else {
      router.push('/profile') // Default for users with no specific role page
    }
  } else {
    router.push('/login')
  }
}, { immediate: true })

const handleLogout = () => {
  localStorage.removeItem('currentUser')
  localStorage.removeItem('currentUsername') // Clear username from localStorage
  currentUser.value = null
  alert('Logged out.')
  router.push('/login')
}
</script>

<template>
  <div id="app">
    <header>
      <h1>Driver Manager System</h1>
      <nav v-if="isLoggedIn">
        <span>Welcome, {{ currentUser.name || currentUser.username }}!</span>
        <router-link to="/profile">Edit Profile</router-link>
        <router-link v-if="isCompany" to="/company">Company Dashboard</router-link>
        <router-link v-if="isDispatcher" to="/dispatcher">Dispatcher Dashboard</router-link>
        <router-link v-if="isDriver" to="/driver">Driver Dashboard</router-link>
        <button @click="handleLogout">Logout</button>
      </nav>
    </header>

    <main>
      <router-view :currentUser="currentUser" @update:currentUser="currentUser = $event" />
    </main>
  </div>
</template>

<style scoped>
#app {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
  font-family: sans-serif;
  background-color: #f4f4f4;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

h1 {
  color: #333;
  margin: 0;
}

nav {
  display: flex;
  align-items: center;
}

nav span {
  margin-right: 1rem;
  font-weight: bold;
  color: #555;
}

nav button,
nav a {
  background-color: #42b983;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  margin-left: 0.5rem; /* Add some space between buttons */
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

nav button:hover,
nav a:hover {
  background-color: #369f75;
}

nav button.logout {
  background-color: #e74c3c;
}

nav button.logout:hover {
  background-color: #c0392b;
}

main {
  padding: 1rem 0;
}

h2 {
  border-bottom: 2px solid #42b983;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  color: #333;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 0.8rem 0.5rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  margin-bottom: 0.5rem;
  border-radius: 4px;
}

li:last-child {
  border-bottom: none;
}

.completed {
  text-decoration: line-through;
  color: #888;
  background-color: #f9f9f9;
}

.error {
  color: #e74c3c;
  background-color: #fbe2e2;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.company-section {
  background-color: #e6f7ff;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border: 1px solid #b3e0ff;
}

.company-section h2 {
  color: #0056b3;
  border-bottom-color: #007bff;
}

.company-section button {
  background-color: #007bff;
}

.company-section button:hover {
  background-color: #0056b3;
}
</style>
