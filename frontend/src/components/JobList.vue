<script setup>

const props = defineProps({
  jobs: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: 'Current Jobs'
  },
  currentUserId: {
    type: String,
    default: null
  },
  isCreator: {
    type: Boolean,
    default: false
  },
  isApplicationList: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['completeJob', 'editJob', 'deleteJob', 'assignJob', 'viewDetails', 'acceptCopiedJob', 'rejectCopiedJob', 'deleteApplication'])

const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'assigned': return 'status-assigned'
    case 'completed': return 'status-completed'
    case 'cancelled': return 'status-cancelled'
    case 'pending_acceptance': return 'status-pending-acceptance'
    case 'application_requested': return 'status-pending-acceptance' // Same color
    case 'accepted': return 'status-accepted'
    case 'rejected': return 'status-rejected'
    case 'superseded': return 'status-superseded'
    default: return ''
  }
}

const formatStatus = (status) => {
  return status.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
};

const handleCompleteJob = (jobId) => {
  if (confirm('Are you sure you want to mark this job as completed?')) {
    emit('completeJob', jobId)
  }
}

const handleEditJob = (job) => {
  emit('editJob', job)
}

const handleDeleteJob = (jobId) => {
  if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
    emit('deleteJob', jobId)
  }
}

const handleAssignJob = (job) => {
  emit('assignJob', job)
}

const handleViewDetails = (job) => {
  emit('viewDetails', job)
}

const handleAcceptCopiedJob = (job) => {
  emit('acceptCopiedJob', job.copied_job_id)
}

const handleRejectCopiedJob = (job) => {
  emit('rejectCopiedJob', job.copied_job_id);
}

const handleDeleteApplication = (copiedJobId) => {
  emit('deleteApplication', copiedJobId);
}

</script>

<template>
  <div class="job-list-container">
    <h3>{{ title }}</h3>
    <div v-if="jobs.length === 0" class="no-jobs">
      No jobs available.
    </div>
    <ul v-else>
      <li v-for="job in jobs" :key="job.id" class="job-item">
        <div class="job-header">
          <h4>
            <template v-if="job.job_type === 'application'">
              Application by {{ job.driver_name }} for Job: {{ job.original_job_id }}
            </template>
            <template v-else>
              {{ job.title }}
            </template>
          </h4>
          <span :class="['job-status', getStatusClass(job.status)]">{{ formatStatus(job.status) }}</span>
        </div>
        <p class="job-description">{{ job.description || 'No description provided.' }}</p>
        <div class="job-details">
          <div v-if="job.company"><strong>Company:</strong> {{ job.company }}</div>
          <div v-if="job.transfer_type"><strong>Transfer Type:</strong> {{ job.transfer_type }}</div>
          <div v-if="job.pick_up_date"><strong>Pick Up Date:</strong> {{ job.pick_up_date }}</div>
          <div v-if="job.pick_up_time"><strong>Pick Up Time:</strong> {{ job.pick_up_time }}</div>
        </div>
        <div class="job-actions">
          <!-- Button for Driver to Complete their own assigned job -->
          <button
            v-if="job.status === 'assigned' && job.assigned_driver_id === currentUserId"
            @click="handleCompleteJob(job.id)"
            class="action-btn complete-btn"
          >
            Complete Job
          </button>

          <!-- Buttons for Dispatcher/Company to manage original jobs -->
          <button
            v-if="isCreator && job.status === 'pending' && job.job_type === 'original'"
            @click="handleAssignJob(job)"
            class="action-btn assign-btn"
          >
            Assign
          </button>
          <button
            v-if="isCreator && job.job_type === 'original'"
            @click="handleEditJob(job)"
            class="action-btn edit-btn"
          >
            Edit
          </button>
          <button
            v-if="isCreator && job.job_type === 'original'"
            @click="handleDeleteJob(job.id)"
            class="action-btn delete-btn"
          >
            Delete
          </button>

          <!-- Buttons for Dispatcher to act on driver applications -->
          <button
            v-if="isCreator && job.job_type === 'application' && job.status === 'application_requested'"
            @click="handleAcceptCopiedJob(job)"
            class="action-btn approve-btn"
          >
            Approve Application
          </button>
          <button
            v-if="isCreator && job.job_type === 'application' && job.status === 'application_requested'"
            @click="handleRejectCopiedJob(job)"
            class="action-btn reject-btn"
          >
            Reject Application
          </button>

          <!-- Buttons for Driver to act on jobs sent to them -->
          <button
            v-if="job.status === 'pending_acceptance' && job.assigned_driver_id === currentUserId"
            @click="handleAcceptCopiedJob(job)"
            class="action-btn approve-btn"
          >
            Accept
          </button>
          <button
            v-if="job.status === 'pending_acceptance' && job.assigned_driver_id === currentUserId"
            @click="handleRejectCopiedJob(job)"
            class="action-btn reject-btn"
          >
            Reject
          </button>

          <!-- Button for Driver to delete their invalid applications -->
          <button
            v-if="isApplicationList && ['superseded', 'rejected', 'accepted'].includes(job.status)"
            @click="handleDeleteApplication(job.copied_job_id)"
            class="action-btn delete-btn"
          >
            Delete Application
          </button>

          <button @click="handleViewDetails(job)" class="action-btn view-details-btn">View Details</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.job-list-container {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.no-jobs {
  text-align: center;
  color: #777;
  padding: 2rem;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

ul {
  list-style: none;
  padding: 0;
}

.job-item {
  border: 1px solid #e0e0e0;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.job-header h4 {
  margin: 0;
  color: #333;
}

.job-status {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
  text-transform: capitalize;
}

.status-pending, .status-pending-acceptance, .status-application_requested {
  background-color: #f0ad4e; /* Orange */
}

.status-assigned {
  background-color: #5bc0de; /* Light Blue */
}

.status-completed, .status-accepted {
  background-color: #5cb85c; /* Green */
}

.status-cancelled, .status-rejected {
  background-color: #d9534f; /* Red */
}

.status-superseded {
  background-color: #6c757d; /* Gray */
}

.job-description {
  color: #666;
  margin-bottom: 1rem;
}

.job-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #eee;
  font-size: 0.9rem;
}

.job-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  color: white;
}

.action-btn:hover {
    box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}

.complete-btn { background-color: #28a745; }
.complete-btn:hover { background-color: #218838; }

.edit-btn { background-color: #007bff; }
.edit-btn:hover { background-color: #0056b3; }

.delete-btn { background-color: #dc3545; }
.delete-btn:hover { background-color: #c82333; }

.assign-btn { background-color: #ffc107; color: #333; }
.assign-btn:hover { background-color: #e0a800; }

.view-details-btn { background-color: #6c757d; }
.view-details-btn:hover { background-color: #5a6268; }

.approve-btn { background-color: #28a745; }
.approve-btn:hover { background-color: #218838; }

.reject-btn { background-color: #dc3545; }
.reject-btn:hover { background-color: #c82333; }

</style>