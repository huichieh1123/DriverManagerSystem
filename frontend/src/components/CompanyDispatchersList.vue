<script setup>

const props = defineProps({
  dispatchers: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['removeDispatcher'])

const handleRemoveDispatcher = (dispatcherId) => {
  if (confirm('Are you sure you want to remove this dispatcher from your company?')) {
    emit('removeDispatcher', dispatcherId)
  }
}
</script>

<template>
  <div class="company-dispatchers-list-container">
    <h3>My Company's Dispatchers</h3>
    <div v-if="dispatchers.length === 0" class="no-dispatchers">
      No dispatchers currently associated with your company.
    </div>
    <ul v-else>
      <li v-for="dispatcher in dispatchers" :key="dispatcher.id" class="dispatcher-item">
        <div class="dispatcher-info">
          <p><strong>Username:</strong> {{ dispatcher.username }}</p>
          <p><strong>Name:</strong> {{ dispatcher.name || 'Not set' }}</p>
          <p v-if="dispatcher.company_name"><strong>Company:</strong> {{ dispatcher.company_name }}</p>
        </div>
        <button @click="handleRemoveDispatcher(dispatcher.id)" class="remove-btn">Remove</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.company-dispatchers-list-container {
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

.no-dispatchers {
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

.dispatcher-item {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fdfdfd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dispatcher-info p {
  margin: 0.2rem 0;
}

.remove-btn {
  background-color: #dc3545;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.remove-btn:hover {
  background-color: #c82333;
}
</style>
