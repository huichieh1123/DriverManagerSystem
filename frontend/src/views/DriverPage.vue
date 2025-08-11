<template>
  <div>
    <h1>Driver Dashboard</h1>
    <InvitationList :invitations="myInvitations" @acceptInvitation="handleAcceptInvitation" @declineInvitation="handleDeclineInvitation" />

    <JobList :jobs="myAssignedJobs" title="My Assigned Jobs" :currentUserId="currentUser.id" @completeJob="handleCompleteJob" @viewDetails="handleViewJobDetails" />
    
    <JobList :jobs="myPendingCopiedJobs" title="Jobs Pending Your Acceptance" :currentUserId="currentUser.id" @acceptCopiedJob="handleAcceptCopiedJob" @rejectCopiedJob="handleRejectCopiedJob" @viewDetails="handleViewJobDetails" />

    <JobList 
      :jobs="myApplications" 
      title="Pending Dispatcher Approval"
      :currentUserId="currentUser.id" 
      :isApplicationList="true" 
      @viewDetails="handleViewJobDetails"
      @deleteApplication="handleDeleteApplication"
    />

    <PublicJobsList :jobs="filteredPublicJobs" title="Public Jobs" @applyForJob="handleApplyForJob" @viewDetails="handleViewJobDetails" />

    <!-- Vehicle Selection Modal for Applying Job -->
    <div v-if="showVehicleSelectModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Select Vehicle for Job Application</h3>
        <div class="form-group">
          <label for="applyVehicleSelect">Choose your vehicle:</label>
          <select id="applyVehicleSelect" v-model="selectedVehicleForApplication">
            <option :value="null">-- Select a Vehicle --</option>
            <option v-for="v in driverVehicles" :key="v.id" :value="v.id">
              {{ v.license_plate }} ({{ v.make }} {{ v.model }})
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="confirmApplyForJob" :disabled="!selectedVehicleForApplication">Confirm Application</button>
          <button @click="cancelApplyForJob" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>

    <JobDetailsModal
      :show="showJobDetailsModal"
      :job="selectedJobForDetails"
      @close="closeJobDetailsModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import JobList from '../components/JobList.vue'
import PublicJobsList from '../components/PublicJobsList.vue'
import JobDetailsModal from '../components/JobDetailsModal.vue'
import InvitationList from '../components/InvitationList.vue'

const props = defineProps({
  currentUser: Object
})

const myAssignedJobs = ref([])
const publicPendingJobs = ref([])
const myPendingCopiedJobs = ref([])
const myApplications = ref([]) // New: store driver's job applications
const driverVehicles = ref([])
const myInvitations = ref([]) // New: to store driver's invitations
const showJobDetailsModal = ref(false)
const selectedJobForDetails = ref(null)

const showVehicleSelectModal = ref(false)
const selectedJobToApply = ref(null)
const selectedVehicleForApplication = ref(null)

// Filter public jobs to exclude those the driver has already applied for
const filteredPublicJobs = computed(() => {
  const appliedJobIds = new Set(myApplications.value.map(app => app.original_job_id));
  return publicPendingJobs.value.filter(job => !appliedJobIds.has(job.id));
});

const fetchDriverData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('driver')) {
    return
  }
  try {
    const driverId = props.currentUser.id;
    const username = props.currentUser.username;

    // Fetch original jobs assigned to this driver
    const assignedResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?assigned_driver_id=${driverId}&job_type=original&username=${username}`
    )
    myAssignedJobs.value = assignedResponse.data

    // Fetch copied jobs pending acceptance for this driver
    const pendingCopiedResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?assigned_driver_id=${driverId}&job_type=copied&status=pending_acceptance&username=${username}`
    )
    myPendingCopiedJobs.value = pendingCopiedResponse.data

    // Fetch this driver's applications
    const applicationsResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?assigned_driver_id=${driverId}&job_type=application&username=${username}`
    );
    myApplications.value = applicationsResponse.data;

    // Fetch all public pending jobs
    const publicResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?is_public=true&status=pending&job_type=original&username=${username}`
    )
    publicPendingJobs.value = publicResponse.data

    // Fetch driver's vehicles
    const vehiclesResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/vehicles/?owner_id=${driverId}&username=${username}`
    )
    driverVehicles.value = vehiclesResponse.data

    // Fetch invitations for driver
    const invitationsResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/drivers/invitations?username=${username}`
    )
    myInvitations.value = invitationsResponse.data

  } catch (err) {
    console.error('Error fetching driver data:', err)
  }
}

watch(
  () => props.currentUser,
  (newVal) => {
    if (newVal) {
      fetchDriverData()
    }
  },
  { immediate: true }
)

const handleAcceptCopiedJob = async (copiedJobId) => {
  if (confirm('Are you sure you want to accept this job?')) {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${copiedJobId}/accept?username=${props.currentUser.username}`
      )
      alert('Job accepted successfully!')
      fetchDriverData()
    } catch (err) {
      console.error('Accept job error:', err.response ? err.response.data : err)
      alert(`Failed to accept job: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const handleRejectCopiedJob = async (copiedJobId) => {
  if (confirm('Are you sure you want to reject this job?')) {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${copiedJobId}/reject?username=${props.currentUser.username}`
      )
      alert('Job rejected.')
      fetchDriverData()
    } catch (err) {
      console.error('Reject job error:', err.response ? err.response.data : err)
      alert(`Failed to reject job: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const handleApplyForJob = (job) => {
  selectedJobToApply.value = job.id
  showVehicleSelectModal.value = true
}

const confirmApplyForJob = async () => {
  if (!selectedJobToApply.value || !selectedVehicleForApplication.value) {
    alert('Please select a job and a vehicle.')
    return
  }
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${selectedJobToApply.value}/apply?username=${props.currentUser.username}&vehicle_id=${selectedVehicleForApplication.value}`
    )
    alert('Job application sent successfully! Waiting for dispatcher approval.')
    fetchDriverData()
    cancelApplyForJob()
  } catch (err) {
    let errorMessage = 'An unknown error occurred.';
    if (err.response && err.response.data && err.response.data.detail) {
        errorMessage = err.response.data.detail;
    } else if (err.message) {
        errorMessage = err.message;
    }
    console.error('Job application error:', err);
    alert(`Job application failed: ${errorMessage}`);
  }
}

const cancelApplyForJob = () => {
  showVehicleSelectModal.value = false
  selectedJobToApply.value = null
  selectedVehicleForApplication.value = null
}

const handleCompleteJob = async (jobId) => {
  if (confirm('Are you sure you want to mark this job as completed?')) {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/drivers/jobs/${jobId}/complete?username=${props.currentUser.username}`
      )
      alert('Job completed successfully!')
      fetchDriverData()
    } catch (err) {
      console.error('Job completion error:', err.response ? err.response.data : err)
      alert(`Job completion failed: ${err.response ? err.response.data.detail : err.message}`)
    }
  }
}

const handleDeleteApplication = async (copiedJobId) => {
  if (confirm('Are you sure you want to delete this application?')) {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/application/${copiedJobId}?username=${props.currentUser.username}`
      );
      alert('Application deleted.');
      fetchDriverData(); // Refresh all data
    } catch (err) {
      console.error('Delete application error:', err.response ? err.response.data : err);
      alert(`Failed to delete application: ${err.response ? err.response.data.detail : 'An unknown error occurred.'}`);
    }
  }
};

const handleAcceptInvitation = async (invitationId) => {
  if (confirm('Are you sure you want to accept this invitation?')) {
    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/drivers/invitations/${invitationId}/accept?username=${props.currentUser.username}`
      );

      // The response.data is now the updated user object from our backend change
      const updatedUser = response.data;

      // Emit event to parent (App.vue) to update the global state
      emit('update:currentUser', updatedUser);
      
      // Also update localStorage
      localStorage.setItem('currentUser', JSON.stringify(updatedUser));

      alert(`You have successfully joined ${updatedUser.company_name}!`);
      
      // Refresh the rest of the driver data (lists of jobs, etc.)
      fetchDriverData();

    } catch (err) {
      console.error('Accept invitation error:', err.response ? err.response.data : err);
      alert(`Failed to accept invitation: ${err.response ? err.response.data.detail : err.message}`);
    }
  }
};

const handleDeclineInvitation = async (invitationId) => {
  if (confirm('Are you sure you want to decline this invitation?')) {
    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/drivers/invitations/${invitationId}/decline?username=${props.currentUser.username}`
      )
      alert(`Invitation from ${response.data.company_name} for ${response.data.invitee_role} declined.`);
      fetchDriverData(); // Refresh data after declining
    } catch (err) {
      console.error('Decline invitation error:', err.response ? err.response.data : err);
      alert(`Failed to decline invitation: ${err.response ? err.response.data.detail : err.message}`);
    }
  }
};

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
h1 {
  text-align: center;
  margin-bottom: 2rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-actions button {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.modal-actions button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}
</style>
