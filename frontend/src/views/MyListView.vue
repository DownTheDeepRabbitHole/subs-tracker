<script setup>
import { onMounted } from 'vue'

import UserPlanList from '@/components/UserPlanList.vue'
import { useSubscriptionManager } from '@/composables'

const {
  userPlans,
  categories,
  fetchUserPlans,
  fetchCategories,
} = useSubscriptionManager()

onMounted(() => {
  fetchUserPlans()
  fetchCategories()
})
</script>

<template>
  <Card class="w-full">
    <template #content>
      <UserPlanList :userPlans="userPlans" :categories="categories" @refresh="fetchUserPlans"/>
    </template>
  </Card>
</template>
