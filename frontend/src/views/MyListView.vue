<script setup>
import UserPlanList from '@/components/UserPlanList.vue'
import Card from 'primevue/card'
</script>

<template>
  <Card class="w-full">
    <template #content>
      <UserPlanList />
    </template>
  </Card>
</template>
