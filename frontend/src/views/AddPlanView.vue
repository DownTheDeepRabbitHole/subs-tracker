<script setup>
import { useRouter } from 'vue-router'
import { useSubscriptionManager, useValidateForms } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { createPlan, addToUserPlans } = useSubscriptionManager()
const { validatePlan, validateUserPlan } = useValidateForms()

const router = useRouter()

const handleCreatePlan = async (form) => {
  if (!validatePlan(form.plan) || !validateUserPlan(form.userPlan)) return

  const newPlanData = await createPlan(form.plan)
  await addToUserPlans(newPlanData.id, form.userPlan.paymentDate, form.userPlan.trackUsage)
  router.push('/my-list')
}
</script>

<template>
  <DetailsCard label="Create Plan" :onSubmit="handleCreatePlan" />
</template>
