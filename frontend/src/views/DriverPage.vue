<template>
  <div>
    <h1>Driver Dashboard</h1>
    <JobList :jobs="myAssignedJobs" title="My Assigned Jobs" :currentUserId="currentUser.id" @completeJob="handleCompleteJob" />
    <PublicJobsList :jobs="publicPendingJobs" @claimJob="handleClaimJob" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import JobList from '../components/JobList.vue'
import PublicJobsList from '../components/PublicJobsList.vue'

const props = defineProps({
  currentUser: Object
})

const myAssignedJobs = ref([])
const publicPendingJobs = ref([])

const fetchDriverData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('driver')) {
    return
  }
  try {
    // Fetch jobs assigned to this driver
    const assignedResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?assigned_driver_id=${props.currentUser.id}`
    )
    myAssignedJobs.value = assignedResponse.data

    // Fetch public pending jobs
    const publicResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?is_public=true&status=pending`
    )
    publicPendingJobs.value = publicResponse.data

  } catch (err) {
    console.error('Error fetching driver data:', err)
  }
}

onMounted(fetchDriverData)
watch(() => props.currentUser, fetchDriverData) // Re-fetch when currentUser changes

const handleClaimJob = async (jobId) => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/drivers/jobs/${jobId}/claim?username=${props.currentUser.username}`
    )
    alert('Job claimed successfully!')
    fetchDriverData() // Refresh job list to reflect changes
  } catch (err) {
    console.error('Job claim error:', err.response ? err.response.data : err)
    alert(`Job claim failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleCompleteJob = async (jobId) => {
  if (confirm('Are you sure you want to mark this job as completed?')) {
    try {
      const response = await axios.put(
        `$ {import.meta.env.VITE_API_URL}/api/v1/drivers/jobs/${jobId}/complete?username=${props.currentUser.username}`
      )
      alert('Job completed successfully!')
      fetchDriverData() // Refresh job list to reflect changes
    } catch (err) {
      console.error('Job completion error:', err.response ? err.response.data : err)
      alert(`Job completion failed: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
</style>
