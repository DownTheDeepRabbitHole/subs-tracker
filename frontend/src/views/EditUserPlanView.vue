<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' 

import { useSubscriptionManager } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchUserPlan, updatePlan, updateUserPlan } = useSubscriptionManager()

const route = useRoute()
const router = useRouter()

const userPlanId = ref(route.params.userPlanId)

const userPlanData = ref({})

onMounted(async () => {
  const data = await fetchUserPlan(userPlanId.value)

  userPlanData.value = {
    plan: {
      id: data.plan_id,
      name: data.plan_name,
      cost: data.cost,
      period: data.period,
      subscription: data.subscription_id,
      freeTrial: data.free_trial,
    },
    userPlan: {
      paymentDate: data.payment_date,
      trackUsage: data.track_usage,
    },
  }
})

const handleEditUserPlan = async (form) => {
  await updatePlan(form.plan)
  await updateUserPlan(form.plan.id, form.userPlan.paymentDate, form.userPlan.trackUsage)

  router.push(-1)
}
</script>

<template>
  <DetailsCard label="Edit User Plan" :data="userPlanData" :onSubmit="handleEditUserPlan">
  </DetailsCard>
</template>
