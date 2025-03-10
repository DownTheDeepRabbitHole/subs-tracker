<script setup>
import { useSubscriptionManager } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { createPlan, addToUserPlans } = useSubscriptionManager()

const handleCreatePlan = async (form) => {
  const newPlanData = await createPlan(form.plan)
  await addToUserPlans(newPlanData.id, form.userPlan.paymentDate, form.userPlan.trackUsage)
}
</script>

<template>
  <DetailsCard :onSubmit="handleCreatePlan"/>
</template>
