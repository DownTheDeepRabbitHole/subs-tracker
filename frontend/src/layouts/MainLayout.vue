<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Topbar from '@/components/Topbar.vue'
import axios from 'axios'
</script>

<template>
  <div class="flex min-h-dvh w-full bg-surface-100">
    <Sidebar />

    <main class="flex flex-col flex-1 min-w-0 relative transition-margin duration-300">
      <Topbar />

      <div class="flex flex-col flex-1 gap-4 px-6 py-6 md:px-14">
        <h1>
          {{ $route.meta.title || 'Default Title' }}
        </h1>
        <RouterView />
      </div>
    </main>
  </div>
</template>
