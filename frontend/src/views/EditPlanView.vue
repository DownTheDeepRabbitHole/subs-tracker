<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' 

import { useSubscriptionManager } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchPlan, updatePlan } = useSubscriptionManager()

const route = useRoute()
const router = useRouter()

const planId = ref(route.params.planId)

const planData = ref({})

onMounted(async () => {
  console.log(planId)
  planData.value = await fetchPlan(planId.value)
})

const handleEditPlan = async (form) => {
  await updatePlan(form.plan)
  router.push(-1)
}
</script>

<template>
  <DetailsCard label="Edit Plan" :data="{plan: planData}" :onSubmit="handleEditPlan" :disabledFields="['userPlan']" />
</template>
