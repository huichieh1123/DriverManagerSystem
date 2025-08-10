<script setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const excelFile = ref(null)
const isUploading = ref(false) // New: loading state for upload
const emit = defineEmits(['jobsUploaded'])

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

  isUploading.value = true // Disable button

  const formData = new FormData()
  formData.append('file', excelFile.value)

  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/dispatchers/jobs/upload?username=${localStorage.getItem('currentUsername')}`,
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
  } finally {
    isUploading.value = false // Re-enable button
  }
}
</script>

<template>
  <div class="batch-upload-container">
    <h3>Batch Upload Jobs (Excel)</h3>
    <div class="batch-upload-section">
      <button @click="handleDownloadTemplate" class="download-template-btn">Download Template</button>
      <div class="form-group file-upload">
        <label for="excelUploadInput">Select Excel File:</label>
        <input type="file" id="excelUploadInput" accept=".xlsx, .xls" @change="handleFileChange" />
      </div>
      <button @click="handleUploadExcel" :disabled="!excelFile || isUploading">Upload Excel</button>
    </div>
  </div>
</template>

<style scoped>
.batch-upload-container {
  background-color: #f8f9fa;
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

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

button {
  background-color: #28a745;
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
  background-color: #218838;
}

button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>
