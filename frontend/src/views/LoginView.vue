<script setup>
import { ref } from 'vue'
import router from '@/router'
import { RouterLink } from 'vue-router'

import axios from 'axios'
import Cookies from 'js-cookie'

import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox'
import Card from '@/components/Card.vue'

const toast = useToast()

const username = ref('')
const password = ref('')
const rememberMe = ref(true)

const onSubmit = async () => {
  try {
    // Make a POST request to the backend login API
    const response = await axios.post('/api/auth/login/', {
      username: username.value,
      password: password.value,
    })

    const { access, refresh } = response.data

    // Set cookies with expiration based on "remember me" checkbox
    if (rememberMe.value) {
      Cookies.set('access_token', access, { expires: 1, path: '' })
      Cookies.set('refresh_token', refresh, { expires: 1, path: '' })
    } else {
      Cookies.set('access_token', access, { path: '' })
      Cookies.set('refresh_token', refresh, { path: '' })
    }

    // Initialize OneSignal and request notification permission
    OneSignalDeferred.push(async function (OneSignal) {
      if (!OneSignal.initialized) {
        await OneSignal.init({
          appId: 'dc6f6c0b-b679-4c19-9db3-021e0cf7a297',
        })
      }

      const id = await getUserId()

      if (id) {
        console.log('Logging in with ID:', id)
        await OneSignal.login(id).catch((error) => {
          console.error('OneSignal login error: ', error)
        })
      }

      OneSignal.Notifications.requestPermission()
    })

    router.push('/')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to log in.', life: 3000 })
    console.log(error)
  }
}

const getUserId = async () => {
  const response = await axios.get('/api/user/get-user-id')
  return response.data['user_id'].toString()
}
</script>

<template>
  <Card class="max-w-md">
    <h2 class="text-center text-2xl font-semibold mb-6 text-text-color dark:text-text-color">Login</h2>

    <form @submit.prevent="onSubmit">
      <div class="mb-4">
        <label for="username" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"> Username </label>
        <InputText inputId="username" v-model="username" placeholder="Enter your username" fluid />
      </div>

      <div class="mb-4">
        <label for="password" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"> Password </label>
        <Password id="password" v-model="password" placeholder="Enter your password" type="password" :feedback="false" ToggleMask fluid />
      </div>

      <div class="mb-6 flex items-center">
        <Checkbox inputId="remember-me" v-model="rememberMe" binary />
        <label for="remember-me" class="ml-2 text-sm">Remember me</label>
      </div>

      <div class="mb-6">
        <Button label="Login" type="submit" icon="pi pi-sign-in" class="w-full p-button-lg p-button-primary" />
      </div>
    </form>

    <div class="text-center mt-4">
      <p class="text-sm">
        New user?
        <RouterLink to="/register" class="text-blue-500 hover:underline">Create account</RouterLink>
      </p>
    </div>
  </Card>
</template>
