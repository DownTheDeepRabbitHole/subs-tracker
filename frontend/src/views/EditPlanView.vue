<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useSubscriptionManager, useValidateForms } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchPlan, updatePlan } = useSubscriptionManager()
const { validatePlan } = useValidateForms()

const route = useRoute()
const router = useRouter()

const planId = ref(route.params.planId)
const planData = ref({})

onMounted(async () => {
  planData.value = await fetchPlan(planId.value)
})

const handleEditPlan = async (form) => {
  if (!validatePlan(form.plan)) return

  await updatePlan(form.plan)
  router.go(-1)
}
</script>

<template>
  <DetailsCard
    label="Edit Plan"
    :data="{ plan: planData }"
    :onSubmit="handleEditPlan"
    :disabledFields="['userPlan']"
  />
</template>
