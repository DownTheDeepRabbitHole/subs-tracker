<script setup>
import axios from 'axios'

import Navbar from './components/Navbar.vue'
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'

// async function permissionChangeListener(permission) {
//   if (permission) {
//     const id = await getUserId()

//     console.log(id.toString())

//     OneSignal.login(id.toString()).catch((error) => {
//       console.error('OneSignal login error: ', error)
//     })
//   }
// }

// OneSignalDeferred.push(function (OneSignal) {
//   OneSignal.Notifications.addEventListener('permissionChange', permissionChangeListener)
// })

// const getUserId = async () => {
//   const response = await axios.get('/api/get-user-id')
//   return response.data['user_id'].toString()
// }
</script>

<template>
  <Toast />
  <Navbar v-if="$route.meta.requiresAuth" />
  <div class="min-h-screen flex justify-center items-center bg-surface-100 dark:bg-surface-900">
    <RouterView />
  </div>
</template>
