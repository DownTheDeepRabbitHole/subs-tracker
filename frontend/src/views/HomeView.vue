<script setup>
import { onMounted, ref } from 'vue'
import { useSubscriptionManager } from '@/composables'

import CategoryStats from '@/components/CategoryStats.vue'
import SpendingStats from '@/components/SpendingStats.vue'
import UserPlanList from '@/components/UserPlanList.vue'
import CardWrapper from '@/components/CardWrapper.vue'
import UserPlanCard from '@/components/UserPlanCard.vue'
import SuccessCard from '@/components/SucessCard.vue'

const { fetchUserPlans } = useSubscriptionManager()

const upcomingPlans = ref([])
const unusedPlans = ref([])

onMounted(() => {
  fetchUpcomingUserPlans()
  fetchUnusedUserPlans()
})

const fetchUpcomingUserPlans = async () => {
  upcomingPlans.value = await fetchUserPlans({ days_until_payment: 7, page_size: 7 })
}

const fetchUnusedUserPlans = async () => {
  unusedPlans.value = await fetchUserPlans({ usage_score: 5, page_size: 6 })
}
</script>

<template>
  <SpendingStats />
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <div class="lg:col-span-2">
      <CategoryStats />
    </div>
    <div class="lg:col-span-1">
      <CardWrapper title="Upcoming Payments">
        <UserPlanList
          :userPlans="upcomingPlans"
          :fields="['plan', 'cost', 'payment_date']"
          @refresh="fetchUpcomingUserPlans"
          :showFilters="false"
          :showHeaders="false"
          :paginator="false"
        />
      </CardWrapper>
    </div>
  </div>

  <h3>Unused Subscriptions</h3>

  <div v-if="unusedPlans.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    <UserPlanCard
      v-for="userPlan in unusedPlans"
      :key="userPlan.id"
      :userPlan="userPlan"
      @refresh="fetchUnusedUserPlans"
    />
  </div>
  <SuccessCard v-else title="Congrats!">You have no unused subscriptions.</SuccessCard>
</template>
