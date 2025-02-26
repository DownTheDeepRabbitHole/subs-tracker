<script setup>
import Sidebar from '@/components/Sidebar.vue'
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
</script>

<template>
  <Toast />
  <div class="flex h-screen">
    <Sidebar v-if="$route.meta.requiresAuth" />

    <main
      class="p-6 w-full"
      :class="{
        'flex justify-center items-center': !$route.meta.requiresAuth,
        'flex-1 flex-col': $route.meta.requiresAuth,
      }"
    >
      <RouterView />
    </main>
  </div>
</template>
