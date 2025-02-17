<script setup>
import { ref } from 'vue'

import router from '@/router'
import { RouterLink } from 'vue-router'
import axios from 'axios'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from '@/components/Card.vue'

const username = ref('')
const password = ref('')
const errorMessage = ref('')

const onSubmit = async () => {
  try {
    // Make a POST request to the backend login API
    const response = await axios.post('http://localhost:8000/api/login/', {
      username: username.value,
      password: password.value,
    })

    // If login is successful, handle the JWT tokens
    const { access, refresh } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    OneSignalDeferred.push(async function (OneSignal) {
      logInUser()
      // OneSignal.User.addEventListener('change', function (event) {
      //   console.log('change', { event })
      //   logInUser()
      // })

      // Request notification permissions
      OneSignal.Notifications.requestPermission()
    })

    OneSignalDeferred.push(async function (OneSignal) {
      const id = await getUserId()

      console.log(id)
      console.log(OneSignal.User.onesignalId)

      await OneSignal.login(id).catch((error) => {
        console.error('OneSignal login error: ', error)
      })
    })

    router.push('/')
  } catch (error) {
    errorMessage.value = 'Invalid username or password'
    console.log(error)
  }
}

const getUserId = async () => {
  const response = await axios.get('/api/get-user-id')
  return response.data['user_id'].toString()
}

const logInUser = async () => {
  const id = await getUserId()

  console.log(id)
  console.log(OneSignal.User.onesignalId)

  await OneSignal.login(id).catch((error) => {
    console.error('OneSignal login error: ', error)
  })
}
</script>

<template>
  <Card class="max-w-md">
    <h2 class="text-center text-2xl font-semibold mb-6 text-text-color dark:text-text-color">Login</h2>

    <form @submit.prevent="onSubmit">
      <div class="mb-4">
        <label for="username" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"> Username </label>
        <InputText id="username" v-model="username" placeholder="Enter your username" fluid />
      </div>

      <div class="mb-4">
        <label for="password" class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"> Password </label>
        <Password id="password" v-model="password" placeholder="Enter your password" type="password" :feedback="false" ToggleMask fluid />
      </div>

      <div class="mb-6">
        <Button label="Login" type="submit" icon="pi pi-sign-in" class="w-full p-button-lg p-button-primary" />
      </div>
    </form>
    <div v-if="errorMessage" class="text-red-500 text-sm text-center">
      {{ errorMessage }}
    </div>

    <div class="text-center mt-4">
      <p class="text-sm">
        New user?
        <RouterLink to="/register" class="text-blue-500 hover:underline">Create account</RouterLink>
      </p>
    </div>
  </Card>
</template>
