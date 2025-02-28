<script setup>
import Button from 'primevue/button'
</script>

<template>
  <div class="bg-white shadow-md sticky top-0 p-3 flex justify-between items-center z-50 w-full">
    <!-- left aligned things (to potentially add later) -->
    <div class="flex-1"></div>

    <div class="flex items-center gap-3">
      <Button icon="pi pi-question-circle" variant="text" rounded aria-label="Help" />

      <Button icon="pi pi-bell" variant="text" rounded aria-label="Notifications" />

      <RouterLink to="/settings">
        <Button icon="pi pi-cog" variant="text" rounded aria-label="Settings"> </Button>
      </RouterLink>

      <Button icon="pi pi-user" variant="text" rounded aria-label="Profile" />
    </div>
  </div>
</template>
