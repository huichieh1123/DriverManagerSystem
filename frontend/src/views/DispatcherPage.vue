<template>
  <div>
    <h1>Dispatcher Dashboard</h1>
    <InvitationList :invitations="myInvitations" @acceptInvitation="handleAcceptInvitation" @declineInvitation="handleDeclineInvitation" />

    <div class="collapsible-form">
      <h2 @click="showCreateJobForm = !showCreateJobForm">Create New Job (click to expand)</h2>
      <JobForm v-if="showCreateJobForm && !editingJob" :currentUser="currentUser" @createJob="handleCreateJob" />
    </div>

    <BatchUploadForm @jobsUploaded="handleJobsUploaded" />

    <div v-if="editingJob" class="edit-job-section">
      <h2>Edit Job</h2>
      <JobForm :initialJobData="editingJob" :isUpdate="true" @updateJob="handleUpdateJob" />
      <button @click="cancelEditingJob">Cancel Edit</button>
    </div>

    <JobList 
      :jobs="jobApplications" 
      title="Driver Job Applications"
      :isCreator="true" 
      :currentUserId="currentUser.id"
      @acceptCopiedJob="handleAcceptCopiedJob" 
      @rejectCopiedJob="handleRejectCopiedJob"
      @viewDetails="handleViewJobDetails" 
    />

    <JobList 
      :jobs="myCreatedJobs" 
      title="My Created Jobs" 
      :isCreator="true" 
      :currentUserId="currentUser.id"
      @editJob="startEditingJob" 
      @deleteJob="handleDeleteJob" 
      @assignJob="startAssigningJob" 
      @viewDetails="handleViewJobDetails" 
    />
    <button @click="handleExportJobs">Export My Created Jobs to Excel</button>
    
    <PublicJobsList :jobs="publicPendingJobs" @viewDetails="handleViewJobDetails" />

    <AssignJobModal
      v-if="showAssignModal && jobToAssign"
      :show="showAssignModal"
      :job="jobToAssign"
      :drivers="availableDrivers"
      @assign="handleAssignJob"
      @close="cancelAssigningJob"
    />

    <JobDetailsModal
      :key="selectedJobForDetails ? selectedJobForDetails.id : 'no-job'"
      :show="showJobDetailsModal"
      :job="selectedJobForDetails"
      @close="closeJobDetailsModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import JobForm from '../components/JobForm.vue'
import BatchUploadForm from '../components/BatchUploadForm.vue'
import JobList from '../components/JobList.vue'
import PublicJobsList from '../components/PublicJobsList.vue'
import InvitationList from '../components/InvitationList.vue'
import AssignJobModal from '../components/AssignJobModal.vue'
import JobDetailsModal from '../components/JobDetailsModal.vue'

const props = defineProps({
  currentUser: Object
})

const myCreatedJobs = ref([])
const jobApplications = ref([])
const publicPendingJobs = ref([])
const myInvitations = ref([])
const editingJob = ref(null)
const showAssignModal = ref(false)
const jobToAssign = ref(null)
const availableDrivers = ref([])
const showCreateJobForm = ref(false)
const showJobDetailsModal = ref(false)
const selectedJobForDetails = ref(null)

const fetchDispatcherData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('dispatcher')) {
    return
  }
  try {
    const username = props.currentUser.username;
    const dispatcherId = props.currentUser.id;
    const companyId = props.currentUser.company_id;

    // Fetch jobs created by this dispatcher (originals only)
    const createdResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?created_by_dispatcher_id=${dispatcherId}&job_type=original&username=${username}`
    )
    myCreatedJobs.value = createdResponse.data;

    // Fetch pending applications for the dispatcher's company
    if (companyId) {
      const applicationsResponse = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/?job_type=application&status=application_requested&company_id=${companyId}&username=${username}`
      );
      jobApplications.value = applicationsResponse.data;
    }

    // Fetch public pending jobs
    const publicResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?is_public=true&status=pending&username=${username}`
    )
    publicPendingJobs.value = publicResponse.data

    // Fetch invitations for dispatcher
    const invitationsResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/invitations?username=${username}`
    )
    myInvitations.value = invitationsResponse.data

    // Fetch all drivers for assignment
    const driversResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/users/?role=driver&username=${username}&include_vehicles=true`
    )
    availableDrivers.value = driversResponse.data

  } catch (err) {
    console.error('Error fetching dispatcher data:', err)
  }
}

const handleAcceptCopiedJob = async (copiedJobId) => {
  if (confirm('Are you sure you want to accept this job application?')) {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${copiedJobId}/accept?username=${props.currentUser.username}`
      )
      alert('Job application accepted successfully!')
      fetchDispatcherData()
    } catch (err) {
      console.error('Accept application error:', err.response ? err.response.data : err)
      alert(`Failed to accept application: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const handleRejectCopiedJob = async (copiedJobId) => {
  if (confirm('Are you sure you want to reject this job application?')) {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${copiedJobId}/reject?username=${props.currentUser.username}`
      )
      alert('Job application rejected.')
      fetchDispatcherData()
    } catch (err) {
      console.error('Reject application error:', err.response ? err.response.data : err)
      alert(`Failed to reject application: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

onMounted(fetchDispatcherData)
watch(() => props.currentUser, fetchDispatcherData, { immediate: true })

const handleCreateJob = async (jobData) => {
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/?username=${props.currentUser.username}`,
      jobData
    )
    alert('Job created successfully!')
    fetchDispatcherData()
  } catch (err) {
    console.error('Job creation error:', err.response ? err.response.data : err)
    alert(`Job creation failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleJobsUploaded = () => {
  fetchDispatcherData()
}

const handleAcceptInvitation = async (invitationId) => {
  try {
    const response = await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/invitations/${invitationId}/accept?username=${props.currentUser.username}`
    )
    alert(`Invitation from ${response.data.company_name} for ${response.data.invitee_role} accepted!`);
    fetchDispatcherData()
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
    alert(`Invitation from ${response.data.company_name} for ${response.data.invitee_role} declined.`);
    fetchDispatcherData()
  } catch (err) {
    console.error('Decline invitation error:', err.response ? err.response.data : err)
    alert(`Failed to decline invitation: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const startEditingJob = (job) => {
  editingJob.value = { ...job }
}

const cancelEditingJob = () => {
  editingJob.value = null
}

const handleUpdateJob = async ({ id, data }) => {
  try {
    await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${id}?username=${props.currentUser.username}`,
      data
    )
    fetchDispatcherData()
  } catch (err) {
    console.error('Job update error:', err.response ? err.response.data : err)
    alert(`Job update failed: ${err.response ? err.response.data.detail : err.message}`)
  } finally {
    editingJob.value = null
  }
}

const handleDeleteJob = async (jobId) => {
  if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}?username=${props.currentUser.username}`
      )
      alert('Job deleted successfully!')
      fetchDispatcherData()
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

const handleAssignJob = async ({ jobId, driverId, vehicleId }) => {
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}/send_to_driver?username=${props.currentUser.username}&driver_id=${driverId}&vehicle_id=${vehicleId}`
    )
    alert('Job sent to driver successfully!')
    cancelAssigningJob()
    fetchDispatcherData()
  } catch (err) {
    console.error('Job assignment error:', err.response ? err.response.data : err)
    alert(`Job assignment failed: ${err.response ? err.response.data.detail : err.message}`)
  }
}

const handleExportJobs = async () => {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/export?username=${props.currentUser.username}`,
      { responseType: 'blob' }
    )
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'jobs_export.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    alert('Jobs exported successfully!')
  } catch (err) {
    console.error('Error exporting jobs:', err.response ? err.response.data : err)
    if (err.response && err.response.data instanceof Blob && err.response.data.type === 'application/json') {
      try {
        const errorText = await err.response.data.text();
        const errorJson = JSON.parse(errorText);
        alert(`Failed to export jobs: ${errorJson.detail || 'An unknown error occurred.'}`);
      } catch (parseError) {
        alert('Failed to export jobs and could not parse the error message.');
      }
    } else {
      alert(`Failed to export jobs: ${err.message}`);
    }
  }
}

const handleViewJobDetails = (job) => {
  selectedJobForDetails.value = job
  showJobDetailsModal.value = true
}

const closeJobDetailsModal = () => {
  showJobDetailsModal.value = false
  selectedJobForDetails.value = null
}
</script>

<style scoped>
h1, h2 {
  text-align: center;
  margin-bottom: 2rem;
}

.collapsible-form h2 {
  cursor: pointer;
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