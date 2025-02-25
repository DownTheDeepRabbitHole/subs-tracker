<script setup>
import { defineProps, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import router from '@/router'

import Cookies from 'js-cookie'

// Define the props and emits
const props = defineProps({
  isCollapsed: Boolean,
})

const emit = defineEmits(['toggle-sidebar'])

// Menu items
const menuItems = [
  { label: 'Home', icon: 'pi pi-home', route: '/' },
  { label: 'Shared List', icon: 'pi pi-users', route: '/shared-list' },
  { label: 'My List', icon: 'pi pi-list', route: '/my-list' },
  { label: 'Add Plan', icon: 'pi pi-plus', route: '/new-plan' },
]

const logout = () => {
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')

  OneSignalDeferred.push(async function (OneSignal) {
    await OneSignal.logout()
    console.log('logged out')
  })

  router.push('/login')
}

// Function to toggle collapse (emit event to parent)
const toggleSidebar = () => {
  emit('toggle-sidebar') // This emits the toggle-sidebar event
}

const isActive = (path) => useRoute().path === path
</script>

<template>
  <aside
    :class="[
      'fixed top-0 left-0 h-screen transition-all duration-300 bg-white border-r dark:bg-gray-800 dark:border-gray-700 flex flex-col',
      props.isCollapsed ? 'w-20' : 'w-64',
    ]"
  >
    <!-- Header & Toggle Button -->
    <div class="flex items-center justify-between p-4">
      <span v-if="!props.isCollapsed" class="text-xl font-bold text-primary">Sub Tracker</span>
      <Button icon="pi pi-bars" class="p-button-text p-2" @click="toggleSidebar" />
    </div>

    <!-- Menu Items -->
    <div class="flex-1 overflow-auto">
      <router-link
        v-for="item in menuItems"
        :key="item.route"
        :to="item.route"
        class="flex items-center gap-4 px-4 py-3 rounded-md transition-all text-lg"
        :class="
          isActive(item.route)
            ? 'bg-primary text-white'
            : 'hover:bg-gray-200 dark:hover:bg-gray-700'
        "
      >
        <i :class="item.icon"></i>
        <span v-if="!props.isCollapsed">{{ item.label }}</span>
      </router-link>
    </div>

    <!-- Logout Button -->
    <div class="p-4 mt-auto">
      <Button
        label="Logout"
        icon="pi pi-sign-out"
        class="w-full p-button-danger flex items-center"
        :class="{ 'justify-center': props.isCollapsed }"
        @click="logout"
      />
    </div>
  </aside>
</template>
