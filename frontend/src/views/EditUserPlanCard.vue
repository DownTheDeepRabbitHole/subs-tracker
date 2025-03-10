<script setup>
import { ref, onMounted } from 'vue'
import { useSubscriptionManager } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchUserPlan, updatePlan, updateUserPlan } = useSubscriptionManager()

const props = defineProps({
  userPlanId: { type: Number, required: true },
})

const userPlanData = ref({})

onMounted(async () => {
  const data = await fetchUserPlan(props.userPlanId)

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
}
</script>

<template>
  <DetailsCard label="Edit User Plan" :data="userPlanData" :onSubmit="handleEditUserPlan">
  </DetailsCard>
</template>
