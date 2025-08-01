<script setup>
import { ref, defineEmits, defineProps, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  initialJobData: {
    type: Object,
    default: null
  },
  isUpdate: {
    type: Boolean,
    default: false
  }
})

const title = ref('')
const description = ref('')
const status = ref('pending') // Default status
const isPublic = ref(false) // New: default to not public
const excelFile = ref(null)

const emit = defineEmits(['createJob', 'jobsUploaded', 'updateJob'])

const jobStatuses = ['pending', 'assigned', 'completed', 'cancelled']

// Watch initialJobData to pre-fill form when in update mode
watch(() => props.initialJobData, (newVal) => {
  if (newVal) {
    title.value = newVal.title || ''
    description.value = newVal.description || ''
    status.value = newVal.status || 'pending'
    isPublic.value = newVal.is_public || false
  } else {
    // Reset form if initialJobData is null (e.g., switching from update to create)
    title.value = ''
    description.value = ''
    status.value = 'pending'
    isPublic.value = false
  }
}, { immediate: true, deep: true })

const handleSubmit = () => {
  if (!title.value) {
    alert('Job title cannot be empty.')
    return
  }

  const jobData = {
    title: title.value,
    description: description.value,
    status: status.value,
    is_public: isPublic.value,
  }

  if (props.isUpdate) {
    emit('updateJob', { id: props.initialJobData.id, data: jobData })
  } else {
    emit('createJob', jobData)
  }
  // Clear form after submission (only for create mode, update mode will be handled by parent)
  if (!props.isUpdate) {
    title.value = ''
    description.value = ''
    status.value = 'pending'
    isPublic.value = false
  }
}

const handleFileChange = (event) => {
  excelFile.value = event.target.files[0]
}

const handleDownloadTemplate = async () => {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/template?username=${localStorage.getItem('currentUsername')}`,
      { responseType: 'blob' } // Important for downloading files
    )
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'job_template.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    alert('Job template downloaded!')
  } catch (err) {
    console.error('Error downloading template:', err.response ? err.response.data : err)
    let displayMessage = `Failed to download template: ${err.message}`;

    if (err.response && err.response.data instanceof Blob && err.response.data.type === 'application/json') {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const errorJson = JSON.parse(e.target.result);
          displayMessage = `Failed to download template: ${errorJson.detail || errorJson.message || JSON.stringify(errorJson, null, 2)}`;
          alert(displayMessage);
        } catch (parseError) {
          console.error('Failed to parse error JSON:', parseError);
          alert(displayMessage); // Fallback to generic message
        }
      };
      reader.onerror = (e) => {
        console.error('FileReader error:', e);
        alert(displayMessage); // Fallback to generic message
      };
      reader.readAsText(err.response.data);
      return; // Important: prevent the synchronous alert below from firing
    } else {
      alert(displayMessage);
    }
  }
}

const handleUploadExcel = async () => {
  if (!excelFile.value) {
    alert('Please select an Excel file to upload.')
    return
  }

  const formData = new FormData()
  formData.append('file', excelFile.value)

  try {
    const response = await axios.post(
      `$ {import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/upload?username=${localStorage.getItem('currentUsername')}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    alert(response.data.message)
    excelFile.value = null // Clear selected file
    document.getElementById('excelUploadInput').value = '' // Clear input
    emit('jobsUploaded') // Notify parent to refresh job list
  } catch (err) {
    console.error('Error uploading Excel:', err.response ? err.response.data : err)
    alert(`Failed to upload Excel: ${err.response ? err.response.data.detail : err.message}`)
  }
}
</script>

<template>
  <div class="job-form-container">
    <h3>{{ isUpdate ? 'Edit Job' : 'Create New Job' }}</h3>
    <div class="form-group">
      <label for="jobTitle">Title:</label>
      <input type="text" id="jobTitle" v-model="title" placeholder="Enter job title" />
    </div>
    <div class="form-group">
      <label for="jobDescription">Description:</label>
      <textarea id="jobDescription" v-model="description" placeholder="Enter job description"></textarea>
    </div>
    <div class="form-group">
      <label for="jobStatus">Status:</label>
      <select id="jobStatus" v-model="status">
        <option v-for="s in jobStatuses" :key="s" :value="s">
          {{ s.charAt(0).toUpperCase() + s.slice(1) }}
        </option>
      </select>
    </div>
    <div class="form-group checkbox-group">
      <input type="checkbox" id="isPublic" v-model="isPublic" />
      <label for="isPublic">Make Public (drivers can claim)</label>
    </div>
    <button @click="handleSubmit">{{ isUpdate ? 'Update Job' : 'Create Job' }}</button>

    <hr class="divider" v-if="!isUpdate" />

    <h3 v-if="!isUpdate">Batch Upload Jobs (Excel)</h3>
    <div class="batch-upload-section" v-if="!isUpdate">
      <button @click="handleDownloadTemplate" class="download-template-btn">Download Template</button>
      <div class="form-group file-upload">
        <label for="excelUploadInput">Select Excel File:</label>
        <input type="file" id="excelUploadInput" accept=".xlsx, .xls" @change="handleFileChange" />
      </div>
      <button @click="handleUploadExcel" :disabled="!excelFile">Upload Excel</button>
    </div>
  </div>
</template>

<style scoped>
.job-form-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.form-group.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.form-group.checkbox-group label {
  margin-bottom: 0;
}

button {
  background-color: #42b983;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  width: 100%;
}

button:hover {
  background-color: #369f75;
}

.divider {
  margin: 2rem 0;
  border: 0;
  border-top: 1px solid #eee;
}

.batch-upload-section {
  margin-top: 1.5rem;
}

.download-template-btn {
  background-color: #007bff;
  margin-bottom: 1rem;
}

.download-template-btn:hover {
  background-color: #0056b3;
}

.file-upload input[type="file"] {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f8f8;
}
</style>
