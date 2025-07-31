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
    type: String, // Pass current user ID to check if job is assigned to them
    default: null
  },
  isCreator: {
    type: Boolean, // Indicates if the current user is a creator (dispatcher/company)
    default: false
  }
})

const emit = defineEmits(['completeJob', 'editJob', 'deleteJob', 'assignJob'])

const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'assigned': return 'status-assigned'
    case 'completed': return 'status-completed'
    case 'cancelled': return 'status-cancelled'
    default: return ''
  }
}

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
          <h4>{{ job.title }}</h4>
          <span :class="['job-status', getStatusClass(job.status)]">{{ job.status.charAt(0).toUpperCase() + job.status.slice(1) }}</span>
        </div>
        <p class="job-description">{{ job.description || 'No description provided.' }}</p>
        <div class="job-meta">
          <span v-if="job.assigned_driver_id">Assigned to Driver ID: {{ job.assigned_driver_id }}</span>
          <span v-if="job.created_by_dispatcher_id">Created by Dispatcher ID: {{ job.created_by_dispatcher_id }}</span>
          <span v-if="job.company_name">Company: {{ job.company_name }}</span>
        </div>
        <div class="job-actions">
          <button
            v-if="job.status === 'assigned' && job.assigned_driver_id === currentUserId"
            @click="handleCompleteJob(job.id)"
            class="complete-btn"
          >
            Complete Job
          </button>
          <button
            v-if="isCreator && (job.created_by_dispatcher_id === currentUserId || (job.company_id && job.company_id === currentUserId)) && job.status === 'pending'"
            @click="handleAssignJob(job)"
            class="assign-btn"
          >
            Assign
          </button>
          <button
            v-if="isCreator && (job.created_by_dispatcher_id === currentUserId || (job.company_id && job.company_id === currentUserId))"
            @click="handleEditJob(job)"
            class="edit-btn"
          >
            Edit
          </button>
          <button
            v-if="isCreator && (job.created_by_dispatcher_id === currentUserId || (job.company_id && job.company_id === currentUserId))"
            @click="handleDeleteJob(job.id)"
            class="delete-btn"
          >
            Delete
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.job-list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fdfdfd;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.job-header h4 {
  margin: 0;
  color: #333;
}

.job-status {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
}

.status-pending {
  background-color: #f0ad4e; /* Orange */
}

.status-assigned {
  background-color: #5bc0de; /* Light Blue */
}

.status-completed {
  background-color: #5cb85c; /* Green */
}

.status-cancelled {
  background-color: #d9534f; /* Red */
}

.job-description {
  color: #666;
  margin-bottom: 1rem;
}

.job-meta {
  font-size: 0.9rem;
  color: #888;
}

.job-meta span {
  margin-right: 1rem;
}

.job-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  justify-content: flex-end;
}

.complete-btn {
  background-color: #28a745;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.complete-btn:hover {
  background-color: #218838;
}

.edit-btn {
  background-color: #007bff;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.edit-btn:hover {
  background-color: #0056b3;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.delete-btn:hover {
  background-color: #c82333;
}

.assign-btn {
  background-color: #ffc107;
  color: #333;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.assign-btn:hover {
  background-color: #e0a800;
}
</style>