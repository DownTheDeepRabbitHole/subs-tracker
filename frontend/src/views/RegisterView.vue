<script setup>
import { reactive } from 'vue'

import router from '@/router'
import axios from 'axios'

import Card from '@/components/Card.vue'

import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

const form = reactive({
  username: '',
  password: '',
})

const handleSubmit = async () => {
  const newUser = {
    username: form.username,
    password: form.password,
  }

  try {
    const response = await axios.post('/api/register/', newUser)

    const { access, refresh } = response.data
    localStorage.setItem('access_token', access) // Store access token in localStorage
    localStorage.setItem('refresh_token', refresh) // Store refresh token in localStorage

    console.log('Registered successfully!')

    router.push('/')
  } catch (error) {
    console.error('Error creating user', error.data)
  }
}
</script>

<template>
  <Card class="max-w-md">
    <h2 class="text-2xl font-semibold text-center mb-6">Create Account</h2>

    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label for="username" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color">Username</label>
        <InputText id="username" v-model="form.username" placeholder="Enter your username" required fluid />
      </div>

      <div class="mb-4">
        <label for="password" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color">Password</label>
        <Password id="password" v-model="form.password" placeholder="Enter your password" toggleMask required fluid />
      </div>

      <div class="mb-6">
        <Button label="Register" type="submit" class="w-full p-button-lg p-button-primary" />
      </div>
    </form>

    <div class="text-center mt-4">
      <p class="text-sm">
        Already have an account?
        <RouterLink to="/login" class="text-blue-500 hover:underline">Sign In</RouterLink>
      </p>
    </div>
  </Card>
</template>

<style>
.full-width {
  width: 100%;
}

.full-width .p-inputtext {
  width: 100%;
}
</style>
