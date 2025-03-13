<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' 

import { useSubscriptionManager, useValidateForms } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchUserPlan, updatePlan, updateUserPlan } = useSubscriptionManager()
const { validatePlan, validateUserPlan } = useValidateForms()

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
  if (!validatePlan(form.plan) || !validateUserPlan(form.userPlan)) return

  await updatePlan(form.plan)
  await updateUserPlan(userPlanId.value, form.userPlan.paymentDate, form.userPlan.trackUsage)

  router.go(-1)
}
</script>

<template>
  <DetailsCard label="Edit User Plan" :data="userPlanData" :onSubmit="handleEditUserPlan">
  </DetailsCard>
</template>
