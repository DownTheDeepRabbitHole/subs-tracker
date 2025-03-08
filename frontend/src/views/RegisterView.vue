<script setup>
import { reactive } from 'vue'

import router from '@/router'
import axios from 'axios'
import Cookies from 'js-cookie'

import { useToast } from 'primevue/usetoast'

const toast = useToast()

const form = reactive({
  username: '',
  password: '',
  rememberMe: true,
})

const handleSubmit = async () => {
  const newUser = {
    username: form.username,
    password: form.password,
  }

  try {
    const response = await axios.post('/api/auth/register/', newUser)

    const { access, refresh } = response.data

    if (form.rememberMe) {
      Cookies.set('access_token', access, { expires: 1, path: '' })
      Cookies.set('refresh_token', refresh, { expires: 1, path: '' })
    } else {
      Cookies.set('access_token', access, { path: '' })
      Cookies.set('refresh_token', refresh, { path: '' })
    }

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Registered successfully!',
      life: 3000,
    })
    console.log('Registered successfully!')

    router.push('/')
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to register account.',
      life: 3000,
    })
    console.error('Error creating user', error.data)
  }
}
</script>

<template>
  <Card class="w-100">
    <template #content>
      <h2 class="text-2xl font-semibold text-center mb-6">Create Account</h2>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label
            for="username"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
            >Username</label
          >
          <InputText
            id="username"
            v-model="form.username"
            placeholder="Enter your username"
            required
            fluid
          />
        </div>

        <div class="mb-4">
          <label
            for="password"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
            >Password</label
          >
          <Password
            id="password"
            v-model="form.password"
            placeholder="Enter your password"
            toggleMask
            required
            fluid
          />
        </div>

        <div class="mb-6 flex items-center">
          <Checkbox inputId="remember-me" v-model="form.rememberMe" binary />
          <label for="remember-me" class="ml-2 text-sm">Remember me</label>
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
    </template>
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
