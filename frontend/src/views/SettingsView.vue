<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useHelpers } from '@/composables'

const { showToast, handleError } = useHelpers()

const settings = ref({
  allow_notifications: false,
  api_key_encrypted: '',
  advance_period: 0,
  unused_threshold: 0,
})

const loading = ref(false)

const fetchSettings = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/user/settings/')
    settings.value = response.data
  } catch (error) {
    handleError('Failed to load settings.', error)
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  loading.value = true
  try {
    await axios.patch('/api/user/settings/', settings.value)
    showToast('success', 'Success', 'Settings saved successfully!')
  } catch (error) {
    handleError('Failed to save settings.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <Card class="w-full">
    <template #title> User Settings </template>
    <template #content>
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-2">
          <Checkbox v-model="settings.allow_notifications" :binary="true" />
          <label>Enable Notifications</label>
        </div>

        <div class="flex flex-col">
          <label>API Key (for Screen Time)</label>
          <InputText v-model="settings.api_key_encrypted" type="password" class="w-full" />
        </div>

        <div class="flex flex-col">
          <label>Advance Period (in months)</label>
          <Slider v-model="settings.advance_period" :min="1" :max="12" class="w-full" />
          <span>{{ settings.advance_period }} months</span>
        </div>

        <div class="flex flex-col">
          <label>Unused Threshold</label>
          <Slider v-model="settings.unused_threshold" :min="0" :max="10" class="w-full" />
          <span>{{ settings.unused_threshold }}</span>
        </div>

        <Button label="Save Settings" icon="pi pi-save" :loading="loading" @click="saveSettings" />
      </div>
    </template>
  </Card>
</template>
