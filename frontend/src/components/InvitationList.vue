<script setup>

const props = defineProps({
  invitations: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['acceptInvitation', 'declineInvitation'])

const handleAccept = (invitationId) => {
  if (confirm('Are you sure you want to accept this invitation?')) {
    emit('acceptInvitation', invitationId)
  }
}

const handleDecline = (invitationId) => {
  if (confirm('Are you sure you want to decline this invitation?')) {
    emit('declineInvitation', invitationId)
  }
}
</script>

<template>
  <div class="invitation-list-container">
    <h3>My Invitations</h3>
    <div v-if="invitations.length === 0" class="no-invitations">
      No invitations received.
    </div>
    <ul v-else>
      <li v-for="invitation in invitations" :key="invitation.id" class="invitation-item">
        <div class="invitation-details">
          <p><strong>From:</strong> {{ invitation.company_name }}</p>
          <p><strong>Status:</strong> <span :class="['status', `status-${invitation.status.toLowerCase()}`]">{{ invitation.status }}</span></p>
        </div>
        <div class="invitation-actions" v-if="invitation.status === 'pending'">
          <button @click="handleAccept(invitation.id)" class="accept-btn">Accept</button>
          <button @click="handleDecline(invitation.id)" class="decline-btn">Decline</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.invitation-list-container {
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

.no-invitations {
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

.invitation-item {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  background-color: #fdfdfd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.invitation-details p {
  margin: 0.2rem 0;
}

.status {
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.status-pending {
  background-color: #ffc107;
  color: #333;
}

.status-accepted {
  background-color: #28a745;
  color: white;
}

.status-declined {
  background-color: #dc3545;
  color: white;
}

.invitation-actions button {
  margin-left: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.accept-btn {
  background-color: #28a745;
  color: white;
}

.accept-btn:hover {
  background-color: #218838;
}

.decline-btn {
  background-color: #dc3545;
  color: white;
}

.decline-btn:hover {
  background-color: #c82333;
}
</style>