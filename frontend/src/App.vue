<script setup>
import { ref } from 'vue'

import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'

import Sidebar from './components/Sidebar.vue'

const isSidebarCollapsed = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<template>
  <Toast />
  <div class="flex min-h-screen bg-surface-100 dark:bg-surface-900">
    <div v-if="$route.meta.requiresAuth" :class="isSidebarCollapsed ? 'w-16' : 'w-64'">
      <Sidebar
        :is-collapsed="isSidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
    </div>

    <div :class="['flex-1', $route.meta.requiresAuth ? 'ml-20' : 'flex justify-center items-center']">
      <RouterView />
    </div>
  </div>
</template>