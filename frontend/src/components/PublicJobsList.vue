<script setup>

const props = defineProps({
  jobs: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['claimJob'])

const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'assigned': return 'status-assigned'
    case 'completed': return 'status-completed'
    case 'cancelled': return 'status-cancelled'
    default: return ''
  }
}

const handleClaimJob = (jobId) => {
  if (confirm('Are you sure you want to claim this job?')) {
    emit('claimJob', jobId)
  }
}
</script>

<template>
  <div class="public-jobs-list-container">
    <h3>Available Public Jobs</h3>
    <div v-if="jobs.length === 0" class="no-jobs">
      No public jobs currently available.
    </div>
    <ul v-else>
      <li v-for="job in jobs" :key="job.id" class="job-item">
        <div class="job-header">
          <h4>{{ job.title }}</h4>
          <span :class="['job-status', getStatusClass(job.status)]">{{ job.status.charAt(0).toUpperCase() + job.status.slice(1) }}</span>
        </div>
        <p class="job-description">{{ job.description || 'No description provided.' }}</p>
        <div class="job-meta">
          <span v-if="job.created_by_dispatcher_id">Created by Dispatcher ID: {{ job.created_by_dispatcher_id }}</span>
          <span v-if="job.company_name">Company: {{ job.company_name }}</span>
        </div>
        <button @click="handleClaimJob(job.id)" class="claim-button">Claim Job</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.public-jobs-list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-top: 2rem;
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
  display: flex;
  flex-direction: column;
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
  margin-bottom: 1rem;
}

.job-meta span {
  margin-right: 1rem;
}

.claim-button {
  background-color: #007bff;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  align-self: flex-end; /* Align button to the right */
  width: auto; /* Override 100% width from global button style */
}

.claim-button:hover {
  background-color: #0056b3;
}
</style>
