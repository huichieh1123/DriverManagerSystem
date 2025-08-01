<template>
  <div>
    <h1>Dispatcher Dashboard</h1>
    <InvitationList :invitations="myInvitations" @acceptInvitation="handleAcceptInvitation" @declineInvitation="handleDeclineInvitation" />

    <JobForm v-if="!editingJob" @createJob="handleCreateJob" @jobsUploaded="handleJobsUploaded" />

    <div v-if="editingJob" class="edit-job-section">
      <h2>Edit Job</h2>
      <JobForm :initialJobData="editingJob" :isUpdate="true" @updateJob="handleUpdateJob" />
      <button @click="cancelEditingJob">Cancel Edit</button>
    </div>

    <JobList :jobs="myCreatedJobs" title="My Created Jobs" @editJob="startEditingJob" @deleteJob="handleDeleteJob" @assignJob="startAssigningJob" :isCreator="true" :currentUserId="currentUser.id" />
    <PublicJobsList :jobs="publicPendingJobs" @claimJob="handleClaimJob" />

    <AssignJobModal
      :show="showAssignModal"
      :job="jobToAssign"
      :drivers="availableDrivers"
      @assign="handleAssignJob"
      @close="cancelAssigningJob"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import JobForm from '../components/JobForm.vue'
import JobList from '../components/JobList.vue'
import PublicJobsList from '../components/PublicJobsList.vue'
import InvitationList from '../components/InvitationList.vue'
import AssignJobModal from '../components/AssignJobModal.vue'

const props = defineProps({
  currentUser: Object
})

const myCreatedJobs = ref([])
const publicPendingJobs = ref([])
const myInvitations = ref([])
const editingJob = ref(null) // State for job being edited
const showAssignModal = ref(false) // New: control assign modal visibility
const jobToAssign = ref(null) // New: job currently being assigned
const availableDrivers = ref([]) // New: list of all drivers

const fetchDispatcherData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('dispatcher')) {
    return
  }
  try {
    // Fetch jobs created by this dispatcher
    const createdResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?created_by_dispatcher_id=${props.currentUser.id}`
    )
    myCreatedJobs.value = createdResponse.data

    // Fetch public pending jobs (for dispatcher to see)
    const publicResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?is_public=true&status=pending`
    )
    publicPendingJobs.value = publicResponse.data

    // Fetch invitations for dispatcher
    const invitationsResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/invitations/me?username=${props.currentUser.username}`
    )
    myInvitations.value = invitationsResponse.data

    // Fetch all drivers for assignment
    const driversResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/users/?role=driver&username=${props.currentUser.username}`
    )
    availableDrivers.value = driversResponse.data

  } catch (err) {
    console.error('Error fetching dispatcher data:', err)
  }
}

onMounted(fetchDispatcherData)
watch(() => props.currentUser, fetchDispatcherData) // Re-fetch when currentUser changes

const handleCreateJob = async (jobData) => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/?username=${props.currentUser.username}`,
      jobData
    )
    alert('Job created successfully!')
    fetchDispatcherData() // Refresh job list
  } catch (err) {
    console.error('Job creation error:', err.response ? err.response.data : err)
    alert(`Job creation failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleJobsUploaded = () => {
  fetchDispatcherData() // Refresh job list after Excel upload
}

const handleClaimJob = async (jobId) => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/drivers/jobs/${jobId}/claim?username=${props.currentUser.username}`
    )
    alert('Job claimed successfully!')
    fetchDispatcherData() // Refresh job list to reflect changes
  } catch (err) {
    console.error('Job claim error:', err.response ? err.response.data : err)
    alert(`Job claim failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleAcceptInvitation = async (invitationId) => {
  try {
    const response = await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/invitations/${invitationId}/accept?username=${props.currentUser.username}`
    )
    alert('Invitation accepted!')
    // Re-fetch current user to update company info immediately
    const userResponse = await axios.get(`${import.meta.env.VITE_API_URL}/api/v1/users/me?username=${props.currentUser.username}`);
    props.currentUser.value = userResponse.data; // Update currentUser prop
    localStorage.setItem('currentUser', JSON.stringify(userResponse.data)); // Update localStorage
    fetchDispatcherData(); // Refresh data after accepting
  } catch (err) {
    console.error('Accept invitation error:', err.response ? err.response.data : err)
    alert(`Failed to accept invitation: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleDeclineInvitation = async (invitationId) => {
  try {
    const response = await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/invitations/${invitationId}/decline?username=${props.currentUser.username}`
    )
    alert('Invitation declined!')
    fetchDispatcherData() // Refresh data after declining
  } catch (err) {
    console.error('Decline invitation error:', err.response ? err.response.data : err)
    alert(`Failed to decline invitation: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const startEditingJob = (job) => {
  editingJob.value = { ...job } // Create a copy to avoid direct mutation
}

const cancelEditingJob = () => {
  editingJob.value = null
}

const handleUpdateJob = async ({ id, data }) => {
  try {
    const response = await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${id}?username=${props.currentUser.username}`,
      data
    )
    //alert('Job updated successfully!')
    editingJob.value = null // Exit editing mode
    fetchDispatcherData() // Refresh job list
  } catch (err) {
    console.error('Job update error:', err.response ? err.response.data : err)
    //alert(`Job update failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleDeleteJob = async (jobId) => {
  if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}?username=${props.currentUser.username}`
      )
      alert('Job deleted successfully!')
      fetchDispatcherData() // Refresh job list
    } catch (err) {
      console.error('Job deletion error:', err.response ? err.response.data : err)
      alert(`Job deletion failed: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const startAssigningJob = (job) => {
  jobToAssign.value = job
  showAssignModal.value = true
}

const cancelAssigningJob = () => {
  showAssignModal.value = false
  jobToAssign.value = null
}

const handleAssignJob = async ({ jobId, driverId }) => {
  try {
    const response = await axios.put(
      `$ {import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}/assign?username=${props.currentUser.username}&driver_id=${driverId}`
    )
    //alert('Job assigned successfully!')
    cancelAssigningJob() // Close modal
    fetchDispatcherData() // Refresh job list
  } catch (err) {
    console.error('Job assignment error:', err.response ? err.response.data : err)
    //alert(`Job assignment failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
.edit-job-section {
  background-color: #f0f8ff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-top: 2rem;
  border: 1px solid #cceeff;
}

.edit-job-section h2 {
  color: #007bff;
  border-bottom-color: #007bff;
}

.edit-job-section button {
  background-color: #6c757d;
  margin-top: 1rem;
}

.edit-job-section button:hover {
  background-color: #5a6268;
}
</style>
