<script setup>
import { useUser } from '@/composables'

const { userStore } = useUser()
</script>

<template>
  <Card class="w-full">
    <template #title> User Profile </template>
    <template #content>
      <div class="flex flex-col gap-6">
        <div class="flex items-center gap-4">
          <img
            :src="userStore.profile?.avatar_url"
            alt="User Avatar"
            class="w-16 h-16 rounded-full"
          />
          <div>
            <h3>
              {{ userStore.profile.first_name }} {{ userStore.profile.last_name }}
            </h3>
            <p class="text-gray-600">{{ userStore.profile.username }}</p>
            <p class="text-gray-600">{{ userStore.profile.email }}</p>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>
