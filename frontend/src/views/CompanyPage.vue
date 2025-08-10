<template>
  <div v-if="currentUser">
    <h1>Company Dashboard</h1>
    <div class="company-section">
      <h2>Invite User to Your Company</h2>
      <div class="form-group">
        <label for="inviteeUsername">Username:</label>
        <input type="text" id="inviteeUsername" v-model="inviteeUsername" placeholder="Enter username to invite" />
      </div>
      <div class="form-group">
        <label for="inviteeRole">Role:</label>
        <select id="inviteeRole" v-model="inviteeRole">
          <option value="dispatcher">Dispatcher</option>
          <option value="driver">Driver</option>
        </select>
      </div>
      <button @click="handleSendInvitation">Send Invitation</button>
    </div>

    <div class="collapsible-form">
      <h2 @click="showCreateJobForm = !showCreateJobForm">Create New Job (click to expand)</h2>
      <JobForm v-if="showCreateJobForm && !editingJob" :currentUser="currentUser" @createJob="handleCreateJob" />
    </div>

    <BatchUploadForm @jobsUploaded="handleJobsUploaded" />

    <CompanyDispatchersList :dispatchers="companyDispatchers" @removeDispatcher="handleRemoveDispatcher" />

    <!-- Placeholder for CompanyDriversList -->
    <div class="company-drivers-list-container">
      <h3>My Company's Drivers</h3>
      <div v-if="companyDrivers.length === 0" class="no-drivers">
        No drivers currently associated with your company.
      </div>
      <ul v-else>
        <li v-for="driver in companyDrivers" :key="driver.id" class="driver-item">
          <div class="driver-info">
            <p><strong>Username:</strong> {{ driver.username }}</p>
            <p><strong>Name:</strong> {{ driver.name || 'Not set' }}</p>
          </div>
          <button @click="handleRemoveDriver(driver.id)" class="remove-btn">Remove</button>
        </li>
      </ul>
    </div>

    <JobList :jobs="companyAllJobs" title="All Jobs in Your Company" @editJob="startEditingJob" @deleteJob="handleDeleteJob" @assignJob="startAssigningJob" @viewDetails="handleViewJobDetails" :isCreator="true" :currentUserId="currentUser.id" />
    <button @click="handleExportJobs">Export Jobs to Excel</button>

    <div v-if="editingJob" class="edit-job-section">
      <h2>Edit Job</h2>
      <JobForm :initialJobData="editingJob" :isUpdate="true" @updateJob="handleUpdateJob" />
      <button @click="cancelEditingJob">Cancel Edit</button>
    </div>

    <AssignJobModal
      v-if="showAssignModal && jobToAssign"
      :show="showAssignModal"
      :job="jobToAssign"
      :drivers="availableDrivers"
      @assign="handleAssignJob"
      @close="cancelAssigningJob"
    />

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
import CompanyDispatchersList from '../components/CompanyDispatchersList.vue'
import JobList from '../components/JobList.vue'
import JobForm from '../components/JobForm.vue'
import BatchUploadForm from '../components/BatchUploadForm.vue'
import AssignJobModal from '../components/AssignJobModal.vue'
import JobDetailsModal from '../components/JobDetailsModal.vue'

const props = defineProps({
  currentUser: Object
})

const companyDispatchers = ref([])
const companyDrivers = ref([]) // New ref for company drivers
const companyAllJobs = ref([])
const inviteeUsername = ref('') // Renamed from dispatcherUsernameToInvite
const inviteeRole = ref('dispatcher') // New ref for selected role
const editingJob = ref(null)
const showAssignModal = ref(false)
const jobToAssign = ref(null)
const availableDrivers = ref([])
const showCreateJobForm = ref(false)
const showJobDetailsModal = ref(false)
const selectedJobForDetails = ref(null)

const fetchCompanyData = async () => {
  if (!props.currentUser || !props.currentUser.roles.includes('company')) {
    return
  }
  try {
    const username = props.currentUser.username;
    const companyId = props.currentUser.id;

    // Fetch dispatchers for company
    const dispatchersResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/companies/users/company_dispatchers?username=${username}`
    )
    companyDispatchers.value = dispatchersResponse.data

    // Fetch drivers for company (new)
    const driversResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/companies/users/company_drivers?username=${username}`
    )
    companyDrivers.value = driversResponse.data

    // Fetch all jobs for the company
    const allCompanyJobsResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/?company_id=${companyId}&username=${username}`
    )
    companyAllJobs.value = allCompanyJobsResponse.data

    // Fetch all drivers for assignment (this is for the AssignJobModal, not company drivers list)
    const allDriversResponse = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/users/?role=driver&username=${username}`
    )
    availableDrivers.value = allDriversResponse.data

  } catch (err) {
    console.error('Error fetching company data:', err)
  }
}

onMounted(fetchCompanyData)
watch(() => props.currentUser, fetchCompanyData) // Re-fetch when currentUser changes

const handleSendInvitation = async () => {
  if (!inviteeUsername.value) {
    alert(`Please enter a ${inviteeRole.value} username.`);
    return;
  }
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/companies/invitations?username=${props.currentUser.username}`,
      { invitee_username: inviteeUsername.value, invitee_role: inviteeRole.value }
    );
    alert(`Invitation sent to ${response.data.invitee_username} (${response.data.invitee_role})!`);
    inviteeUsername.value = ''; // Clear input
  } catch (err) {
    console.error('Send invitation error:', err.response ? err.response.data : err);
    alert(`Failed to send invitation: ${err.response ? err.response.data.detail : err.message}`);
  }
};

const handleRemoveDispatcher = async (dispatcherId) => {
  if (confirm('Are you sure you want to remove this dispatcher from your company?')) {
    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/companies/users/${dispatcherId}/remove_company?username=${props.currentUser.username}`
      );
      alert(`Dispatcher ${response.data.username} removed from company.`);
      fetchCompanyData(); // Refresh the list of dispatchers
    } catch (err) {
      console.error('Remove dispatcher error:', err.response ? err.response.data : err);
      alert(`Failed to remove dispatcher: ${err.response ? err.response.data.detail : err.message}`);
    }
  }
};

const handleRemoveDriver = async (driverId) => {
  if (confirm('Are you sure you want to remove this driver from your company?')) {
    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/companies/users/${driverId}/remove_driver_company?username=${props.currentUser.username}`
      );
      alert(`Driver ${response.data.username} removed from company.`);
      fetchCompanyData(); // Refresh the list of drivers
    } catch (err) {
      console.error('Remove driver error:', err.response ? err.response.data : err);
      alert(`Failed to remove driver: ${err.response ? err.response.data.detail : err.message}`);
    }
  }
};

const startEditingJob = (job) => {
  editingJob.value = { ...job };
};

const cancelEditingJob = () => {
  editingJob.value = null;
};

const handleUpdateJob = async ({ id, data }) => {
  try {
    await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${id}?username=${props.currentUser.username}`,
      data
    );
    alert('Job updated successfully!');
    editingJob.value = null;
    fetchCompanyData();
  } catch (err) {
    console.error('Job update error:', err.response ? err.response.data : err);
    alert(`Job update failed: ${err.response ? err.response.data.detail : err.message}`);
  }
};

const handleDeleteJob = async (jobId) => {
  if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}?username=${props.currentUser.username}`
      );
      alert('Job deleted successfully!');
      fetchCompanyData();
    } catch (err) {
      console.error('Job deletion error:', err.response ? err.response.data : err);
      alert(`Job deletion failed: ${err.response ? err.response.data.detail : err.message}`);
    }
  }
};

const startAssigningJob = (job) => {
  jobToAssign.value = job;
  showAssignModal.value = true;
};

const cancelAssigningJob = () => {
  showAssignModal.value = false;
  jobToAssign.value = null;
};

const handleAssignJob = async ({ jobId, driverId }) => {
  try {
    await axios.put(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/${jobId}/assign?username=${props.currentUser.username}&driver_id=${driverId}`
    );
    alert('Job assigned successfully!');
    cancelAssigningJob();
    fetchCompanyData();
  } catch (err) {
    console.error('Job assignment error:', err.response ? err.response.data : err);
    alert(`Job assignment failed: ${err.response ? err.response.data.detail : err.message}`);
  }
};

const handleExportJobs = async () => {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/jobs/export?username=${props.currentUser.username}`,
      { responseType: 'blob' }
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'jobs_export.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    alert('Jobs exported successfully!');
  } catch (err) {
    console.error('Error exporting jobs:', err.response ? err.response.data : err);
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
};

const handleJobsUploaded = () => {
  fetchCompanyData();
};

const handleCreateJob = async (jobData) => {
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/?username=${props.currentUser.username}`,
      jobData
    );
    alert('Job created successfully!');
    fetchCompanyData();
  } catch (err) {
    console.error('Job creation error:', err.response ? err.response.data : err);
    alert(`Job creation failed: ${err.response ? err.response.data.detail : err.message}`);
  }
};

const handleViewJobDetails = (job) => {
  selectedJobForDetails.value = job;
  showJobDetailsModal.value = true;
};

const closeJobDetailsModal = () => {
  showJobDetailsModal.value = false;
  selectedJobForDetails.value = null;
};
</script>

<style scoped>
h1, h2 {
  text-align: center;
  margin-bottom: 2rem;
}

.collapsible-form h2 {
  cursor: pointer;
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

.form-group select {
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

.company-drivers-list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-top: 2rem;
}

.company-drivers-list-container h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.company-drivers-list-container .no-drivers {
  text-align: center;
  color: #777;
  padding: 2rem;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

.company-drivers-list-container ul {
  list-style: none;
  padding: 0;
}

.company-drivers-list-container .driver-item {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fdfdfd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.company-drivers-list-container .driver-info p {
  margin: 0.2rem 0;
}

.company-drivers-list-container .remove-btn {
  background-color: #dc3545;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.company-drivers-list-container .remove-btn:hover {
  background-color: #c82333;
}
</style>