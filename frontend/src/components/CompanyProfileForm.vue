<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ company_name: '', company_address: '', contact_person: '' })
  }
})

const companyName = ref(props.initialData.company_name)
const companyAddress = ref(props.initialData.company_address)
const contactPerson = ref(props.initialData.contact_person)

const emit = defineEmits(['update'])

watch(() => props.initialData, (newVal) => {
  companyName.value = newVal.company_name
  companyAddress.value = newVal.company_address
  contactPerson.value = newVal.contact_person
}, { deep: true, immediate: true })

const updateProfile = () => {
  emit('update', {
    company_name: companyName.value,
    company_address: companyAddress.value,
    contact_person: contactPerson.value
  })
}

// Emit update whenever input changes
watch([companyName, companyAddress, contactPerson], updateProfile)
</script>

<template>
  <div class="profile-form-section">
    <h3>Company Profile</h3>
    <div class="form-group">
      <label for="companyName">Company Name:</label>
      <input type="text" id="companyName" v-model="companyName" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="companyAddress">Company Address:</label>
      <input type="text" id="companyAddress" v-model="companyAddress" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="contactPerson">Contact Person:</label>
      <input type="text" id="contactPerson" v-model="contactPerson" @input="updateProfile" />
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
