<script setup>
import HighestSpending from '@/components/HighestSpending.vue';
import SpendingCard from '@/components/SpendingCard.vue';
import UserPlanCard from '@/components/UserPlanCard.vue'

// Test data with two user plans
const testUserPlans = [
  {
    id: 1,
    payment_date: '2025-03-10T00:00:00Z',
    total_spent: 120.5,
    track_usage: true,
    usage_score: 7,
    cost: 30.0,
    plan_name: 'Premium',
    period: 'month',
    subscription_name: 'Netflix',
    icon_url: 'https://example.com/netflix-icon.png',
  },
  {
    id: 2,
    payment_date: '2025-04-15T00:00:00Z',
    total_spent: 85.0,
    track_usage: false,
    usage_score: 5,
    cost: 20.0,
    plan_name: 'Basic',
    period: 'month',
    subscription_name: 'Spotify',
    icon_url: 'https://example.com/spotify-icon.png',
  },
]
</script>

<template>
  <!-- Loop through the user plans array and render a UserPlanCard for each -->
  <div v-for="userPlan in testUserPlans" :key="userPlan.id">
    <UserPlanCard :userPlan="userPlan" />
  </div>
  <SpendingCard />
  <HighestSpending />
</template>
