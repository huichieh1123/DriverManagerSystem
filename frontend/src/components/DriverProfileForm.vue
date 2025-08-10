<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      chinese_name: '',
      english_name: '',
      id_card_number: '',
      phone_number: '',
      gender: '',
      birth_date: '',
      license_valid_date: '',
      license_review_date: '',
      license_type: '',
      gmail: ''
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
    <h3>Driver Profile</h3>
    <div v-if="companyName" class="form-group">
      <label for="company_name">隸屬公司:</label>
      <input type="text" id="company_name" :value="companyName" readonly style="background-color: #eee;" />
    </div>
    <div class="form-group">
      <label for="chinese_name">中文姓名:</label>
      <input type="text" id="chinese_name" v-model="profile.chinese_name" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="english_name">英文簡稱 (非必):</label>
      <input type="text" id="english_name" v-model="profile.english_name" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="id_card_number">身分證號:</label>
      <input type="text" id="id_card_number" v-model="profile.id_card_number" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="phone_number">手機號碼:</label>
      <input type="text" id="phone_number" v-model="profile.phone_number" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="gender">性別:</label>
      <input type="text" id="gender" v-model="profile.gender" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="birth_date">出生年月:</label>
      <input type="date" id="birth_date" v-model="profile.birth_date" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="license_valid_date">駕照有效日:</label>
      <input type="date" id="license_valid_date" v-model="profile.license_valid_date" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="license_review_date">駕照審驗日:</label>
      <input type="date" id="license_review_date" v-model="profile.license_review_date" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="license_type">駕照種類:</label>
      <select id="license_type" v-model="profile.license_type" @change="updateProfile">
        <option value="" disabled>-- 請選擇 --</option>
        <option value="職小客">職小客</option>
        <option value="職大客">職大客</option>
        <option value="職大貨">職大貨</option>
      </select>
    </div>
    <div class="form-group">
      <label for="gmail">G MAIL:</label>
      <input type="text" id="gmail" v-model="profile.gmail" @input="updateProfile" />
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
