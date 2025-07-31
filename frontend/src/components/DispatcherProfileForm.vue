<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ dispatch_area: '', contact_phone: '' })
  }
})

const dispatchArea = ref(props.initialData.dispatch_area)
const contactPhone = ref(props.initialData.contact_phone)

const emit = defineEmits(['update'])

watch(() => props.initialData, (newVal) => {
  dispatchArea.value = newVal.dispatch_area
  contactPhone.value = newVal.contact_phone
}, { deep: true, immediate: true })

const updateProfile = () => {
  emit('update', {
    dispatch_area: dispatchArea.value,
    contact_phone: contactPhone.value
  })
}

// Emit update whenever input changes
watch([dispatchArea, contactPhone], updateProfile)
</script>

<template>
  <div class="profile-form-section">
    <h3>Dispatcher Profile</h3>
    <div class="form-group">
      <label for="dispatchArea">Dispatch Area:</label>
      <input type="text" id="dispatchArea" v-model="dispatchArea" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="contactPhone">Contact Phone:</label>
      <input type="text" id="contactPhone" v-model="contactPhone" @input="updateProfile" />
    </div>
  </div>
</template>

<style scoped>
.profile-form-section {
  border: 1px solid #eee;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1.5rem;
  background-color: #f9f9f9;
}

h3 {
  color: #42b983;
  margin-top: 0;
  margin-bottom: 1rem;
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
</style>
