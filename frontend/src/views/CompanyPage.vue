<template>
  <div>
    <h1>Company Dashboard</h1>
    <div class="company-section">
      <h2>Invite Dispatcher to Your Company</h2>
      <div class="form-group">
        <label for="dispatcherUsername">Dispatcher Username:</label>
        <input type="text" id="dispatcherUsername" v-model="dispatcherUsernameToInvite" placeholder="Enter dispatcher username" />
      </div>
      <button @click="handleSendInvitation">Send Invitation</button>
    </div>

    <CompanyDispatchersList :dispatchers="companyDispatchers" @removeDispatcher="handleRemoveDispatcher" />

    <JobList :jobs="companyAllJobs" title="All Jobs in Your Company" @editJob="startEditingJob" @deleteJob="handleDeleteJob" @assignJob="startAssigningJob" :isCreator="true" :currentUserId="currentUser.id" />

    <div v-if="editingJob" class="edit-job-section">
      <h2>Edit Job</h2>
      <JobForm :initialJobData="editingJob" :isUpdate="true" @updateJob="handleUpdateJob" />
      <button @click="cancelEditingJob">Cancel Edit</button>
    </div>

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
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import CompanyDispatchersList from '../components/CompanyDispatchersList.vue'
import JobList from '../components/JobList.vue'
import JobForm from '../components/JobForm.vue'
import AssignJobModal from '../components/AssignJobModal.vue'

const props = defineProps({
  currentUser: Object
})

const companyDispatchers = ref([])
const companyAllJobs = ref([])
const dispatcherUsernameToInvite = ref('')
const editingJob = ref(null) // State for job being edited
const showAssignModal = ref(false) // New: control assign modal visibility
const jobToAssign = ref(null) // New: job currently being assigned
const availableDrivers = ref([]) // New: list of all drivers

const fetchCompanyData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('company')) {
    return
  }
  try {
    // Fetch dispatchers for company
    const dispatchersResponse = await axios.get(
      `http://127.0.0.1:8000/api/v1/companies/users/company_dispatchers?username=${props.currentUser.username}`
    )
    companyDispatchers.value = dispatchersResponse.data

    // Fetch all jobs for the company
    const allCompanyJobsResponse = await axios.get(
      `http://127.0.0.1:8000/api/v1/jobs/?company_id=${props.currentUser.id}`
    )
    companyAllJobs.value = allCompanyJobsResponse.data

    // Fetch all drivers for assignment
    const driversResponse = await axios.get(
      `http://127.0.0.1:8000/api/v1/users/?role=driver&username=${props.currentUser.username}`
    )
    availableDrivers.value = driversResponse.data

  } catch (err) {
    console.error('Error fetching company data:', err)
  }
}

onMounted(fetchCompanyData)
watch(() => props.currentUser, fetchCompanyData) // Re-fetch when currentUser changes

const handleSendInvitation = async () => {
  if (!dispatcherUsernameToInvite.value) {
    alert('Please enter a dispatcher username.')
    return
  }
  try {
    // First, check the target dispatcher's current status
    const targetDispatcherResponse = await axios.get(
      `http://127.0.0.1:8000/api/v1/users/me?username=${dispatcherUsernameToInvite.value}`
    );
    const targetDispatcher = targetDispatcherResponse.data;

    if (!targetDispatcher || !targetDispatcher.roles.includes('dispatcher')) {
      alert('Target user is not a dispatcher or does not exist.');
      return;
    }

    if (targetDispatcher.dispatcher_association_status === 'associated') {
      alert(`Dispatcher ${targetDispatcher.username} is already associated with a company.`);
      return;
    }

    const response = await axios.post(
      `http://127.0.0.1:8000/api/v1/companies/invitations/send?username=${props.currentUser.username}`,
      { dispatcher_username: dispatcherUsernameToInvite.value }
    )
    alert(`Invitation sent to ${response.data.dispatcher_username} (ID: ${response.data.id})!`)
    dispatcherUsernameToInvite.value = '' // Clear input
  } catch (err) {
    console.error('Send invitation error:', err.response ? err.response.data : err)
    alert(`Failed to send invitation: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleRemoveDispatcher = async (dispatcherId) => {
  if (confirm('Are you sure you want to remove this dispatcher from your company?')) {
    try {
      const response = await axios.put(
        `http://127.0.0.1:8000/api/v1/companies/users/${dispatcherId}/remove_company?username=${props.currentUser.username}`
      )
      alert(`Dispatcher ${response.data.username} removed from company.`)
      fetchCompanyData() // Refresh the list of dispatchers
    } catch (err) {
      console.error('Remove dispatcher error:', err.response ? err.response.data : err)
      alert(`Failed to remove dispatcher: ${err.response ? err.response.data.detail : err.message}`)
    }
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
      `http://127.0.0.1:8000/api/v1/jobs/${id}?username=${props.currentUser.username}`,
      data
    )
    alert('Job updated successfully!')
    editingJob.value = null // Exit editing mode
    fetchCompanyData() // Refresh job list
  } catch (err) {
    console.error('Job update error:', err.response ? err.response.data : err)
    alert(`Job update failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleDeleteJob = async (jobId) => {
  if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
    try {
      await axios.delete(
        `http://127.0.0.1:8000/api/v1/jobs/${jobId}?username=${props.currentUser.username}`
      )
      alert('Job deleted successfully!')
      fetchCompanyData() // Refresh job list
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
    alert('Job assigned successfully!')
    cancelAssigningJob() // Close modal
    fetchCompanyData() // Refresh job list
  } catch (err) {
    console.error('Job assignment error:', err.response ? err.response.data : err)
    alert(`Job assignment failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
.company-section {
  background-color: #e6f7ff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
