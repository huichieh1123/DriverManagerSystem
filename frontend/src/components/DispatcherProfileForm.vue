<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      contact_name: '',
      contact_phone: '',
      work_nature: '',
      bank_accounts: []
    })
  }
})

const profile = ref({ ...props.initialData })

const emit = defineEmits(['update'])

watch(() => props.initialData, (newVal) => {
  profile.value = { ...newVal, bank_accounts: newVal.bank_accounts || [] }
}, { deep: true, immediate: true })

const updateProfile = () => {
  emit('update', profile.value)
}

const addBankAccount = () => {
  profile.value.bank_accounts.push({ bank_code: '', account_number: '' })
  updateProfile()
}

const removeBankAccount = (index) => {
  profile.value.bank_accounts.splice(index, 1)
  updateProfile()
}

// Emit update whenever any profile data changes
watch(profile, updateProfile, { deep: true })
</script>

<template>
  <div class="profile-form-section">
    <h3>Dispatcher Profile</h3>
    <div class="form-group">
      <label for="contact_name">姓名:</label>
      <input type="text" id="contact_name" v-model="profile.contact_name" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="contact_phone">聯繫電話:</label>
      <input type="text" id="contact_phone" v-model="profile.contact_phone" @input="updateProfile" />
    </div>
    <div class="form-group">
      <label for="work_nature">工作性質:</label>
      <select id="work_nature" v-model="profile.work_nature" @change="updateProfile">
        <option value="" disabled>-- 請選擇 --</option>
        <option value="調度">調度</option>
        <option value="派單">派單</option>
        <option value="派單與調度">派單與調度</option>
        <option value="夜間值班">夜間值班</option>
        <option value="日間值班">日間值班</option>
      </select>
    </div>

    <h4>銀行帳號</h4>
    <div v-for="(account, index) in profile.bank_accounts" :key="index" class="bank-account-group">
      <div class="form-group">
        <label :for="`bank_code_${index}`">銀行代碼:</label>
        <input :id="`bank_code_${index}`" type="text" v-model="account.bank_code" @input="updateProfile" />
      </div>
      <div class="form-group">
        <label :for="`account_number_${index}`">銀行帳號:</label>
        <input :id="`account_number_${index}`" type="text" v-model="account.account_number" @input="updateProfile" />
      </div>
      <button @click="removeBankAccount(index)" class="remove-btn">移除</button>
    </div>
    <button @click="addBankAccount" class="add-btn">增加銀行帳號</button>
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

h3, h4 {
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

.bank-account-group {
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.add-btn, .remove-btn {
  background-color: #007bff;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  margin-top: 0.5rem;
}

.add-btn:hover, .remove-btn:hover {
  background-color: #0056b3;
}

.remove-btn {
  background-color: #dc3545;
}

.remove-btn:hover {
  background-color: #c82333;
}
</style>
