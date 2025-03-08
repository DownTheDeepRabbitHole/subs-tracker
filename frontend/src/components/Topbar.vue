<script setup></script>

<template>
  <Toolbar class="bg-white rounded-none border-0 sticky top-0 p-3 z-10">
    <template #start>
      <!-- Left aligned things (to potentially add later) -->
      <div class="flex-1"></div>
    </template>

    <template #end>
      <div class="flex items-center gap-3">
        <Button icon="pi pi-question-circle" variant="text" size="large" aria-label="Help" />

        <Button icon="pi pi-bell" variant="text" size="large" aria-label="Notifications" />

        <RouterLink to="/settings">
          <Button icon="pi pi-cog" variant="text" size="large" aria-label="Settings" />
        </RouterLink>

        <RouterLink to="/profile">
          <Button icon="pi pi-user" variant="text" size="large" aria-label="Profile" />
        </RouterLink>
      </div>
    </template>
  </Toolbar>
</template>
