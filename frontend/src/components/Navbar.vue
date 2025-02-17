<script setup>
import router from '@/router'
import { RouterLink, useRoute } from 'vue-router'

import Button from 'primevue/button'

const isActiveLink = (routePath) => {
  const route = useRoute()
  return route.path === routePath
}

const logout = () => {
  // Remove the access token from localStorage
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')

  OneSignalDeferred.push(async function (OneSignal) {
    await OneSignal.logout()
    console.log("logged out")
  })

  // Redirect the user to the login page
  router.push('/login')
}
</script>

<template>
  <nav class="bg-p-surface-0 border-b">
    <div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
      <div class="flex h-20 items-center justify-between">
        <div class="flex flex-1 items-center justify-center md:items-stretch md:justify-start">
          <RouterLink class="flex flex-shrink-0 items-center mr-4" to="/">
            <span class="hidden md:block text-primary text-2xl font-bold ml-2">Sub Tracker</span>
          </RouterLink>
          <div class="md:ml-auto">
            <div class="flex space-x-2">
              <RouterLink to="/" class="nav-link" :class="{ active: isActiveLink('/') }"> Home </RouterLink>
              <RouterLink to="/shared-list" class="nav-link" :class="{ active: isActiveLink('/shared-list') }"> Shared List </RouterLink>
              <RouterLink to="/my-list" class="nav-link" :class="{ active: isActiveLink('/my-list') }"> My List </RouterLink>
              <Button @click="logout" class="text-black bg-white hover:bg-accent-dark hover:text-white">Logout</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style lang="postcss" scoped>
.nav-link {
  @apply px-3 py-2 rounded-md text-black;

  &:hover {
    @apply bg-accent-dark text-white;
  }

  &.active {
    @apply bg-accent text-white;
  }
}
</style>
