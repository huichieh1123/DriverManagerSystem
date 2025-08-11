<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  job: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const allJobFields = [
  { key: 'company', label: 'Company' },
  { key: 'transfer_type', label: 'Transfer Type' },
  { key: 'pick_up_date', label: 'Pick Up Date' },
  { key: 'pick_up_time', label: 'Pick Up Time' },
  { key: 'flight_number', label: 'Flight Number' },
  { key: 'passenger_name', label: 'Passenger Name' },
  { key: 'phone_number', label: 'Phone Number' },
  { key: 'num_of_passenger', label: 'No. of Passenger' },
  { key: 'from_location', label: 'From' },
  { key: 'to_location', label: 'To' },
  { key: 'additional_services', label: 'Additional Services' },
  { key: 'special_requirements', label: 'Special Requirements' },
  { key: 'other_contact_info', label: 'Other Contact Information' },
  { key: 'order_number', label: 'Order Number' },
  { key: 'total_price', label: 'Total Price' },
  { key: 'email', label: 'E-mail' },
  { key: 'driver_name', label: '駕駛' },
  { key: 'driver_phone', label: '電話' },
  { key: 'vehicle_number', label: '車號' },
  { key: 'vehicle_model', label: '廠牌 (Make)' },
  { key: 'vehicle_type', label: '車型 (Model)' },
  { key: 'is_public', label: '是否外包' },
  { key: 'status', label: 'Status' },
  { key: 'assigned_driver_id', label: 'Assigned Driver ID' },
  { key: 'created_by_dispatcher_id', label: 'Created by Dispatcher ID' },
  { key: 'company_id', label: 'Company ID' },
  { key: 'company_name', label: 'Company Name' },
  { key: 'id', label: 'Job ID' },
]

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div v-if="job" class="modal-content">
      <h3>Job Details: {{ job.order_number || job.id }}</h3>
      <div class="details-grid">
        <template v-for="field in allJobFields" :key="field.key">
          <div class="detail-item">
            <strong>{{ field.label }}:</strong>
            <span>
              {{
                field.key === 'is_public'
                  ? (job[field.key] ? '是' : '否')
                  : (field.key === 'status'
                      ? (job[field.key] ? (job[field.key].charAt(0).toUpperCase() + job[field.key].slice(1)) : '')
                      : (job[field.key] || ''))
              }}
            </span>
          </div>
        </template>
      </div>
      <button @click="handleClose" class="close-btn">Close</button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 600px;
  max-width: 90%;
  max-height: 90vh; /* Limit height */
  overflow-y: auto; /* Enable scrolling for long content */
  display: flex;
  flex-direction: column;
}

h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  text-align: center;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  background-color: #f8f8f8;
  padding: 0.8rem;
  border-radius: 4px;
  border: 1px solid #eee;
}

.detail-item strong {
  display: block;
  color: #555;
  margin-bottom: 0.2rem;
  font-size: 0.9rem;
}

.detail-item span {
  color: #333;
  font-size: 1rem;
  word-wrap: break-word; /* Break long words */
}

.close-btn {
  background-color: #6c757d;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  align-self: flex-end; /* Align button to the right */
  margin-top: 1rem;
}

.close-btn:hover {
  background-color: #5a6268;
}
</style>
