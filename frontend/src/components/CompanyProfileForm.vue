<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      company_name: '',
      tax_id: '',
      admin_line_id: '',
      address: '',
      phone_number: ''
    })
  }
})

const profile = ref({ ...props.initialData })

const emit = defineEmits(['update'])

watch(() => props.initialData, (newVal) => {
  profile.value = { ...newVal }
}, { deep: true, immediate: true })

const updateProfile = () => {
  emit('update', profile.value)
}

// Emit update whenever any profile data changes
watch(profile, updateProfile, { deep: true })
</script>

<template>
  <div class="profile-form-section">
    <h3>Company Profile</h3>
    <div class="form-group">
      <label for="company_name">租車公司名稱:</label>
      <input type="text" id="company_name" v-model="profile.company_name" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="tax_id">車行統編:</label>
      <input type="text" id="tax_id" v-model="profile.tax_id" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="admin_line_id">管理者 LINE ID:</label>
      <input type="text" id="admin_line_id" v-model="profile.admin_line_id" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="address">車行地址:</label>
      <input type="text" id="address" v-model="profile.address" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="phone_number">車行電話:</label>
      <input type="text" id="phone_number" v-model="profile.phone_number" @input="updateProfile" />
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
