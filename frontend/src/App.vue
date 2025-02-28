<script setup>
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'

import Sidebar from '@/components/Sidebar.vue'
import Toolbar from './components/Toolbar.vue'
</script>

<template>
  <Toast />
  <div class="flex h-screen w-screen overflow-x-hidden">
    <Sidebar v-if="$route.meta.requiresAuth" />

    <main class="flex flex-col flex-1 min-w-0 relative" >
      <Toolbar v-if="$route.meta.requiresAuth" />
      <div
        class="flex flex-1 overflow-auto p-4 bg-surface-200"
        :class="$route.meta.requiresAuth ? '' : 'items-center justify-center'"
      >
        <RouterView />
      </div>
    </main>
  </div>
</template>
