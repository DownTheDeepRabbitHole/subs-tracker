<script setup>
import { ref, onMounted } from 'vue'
import { useSubscriptionManager } from '@/composables'
import DetailsCard from '@/components/DetailsCard.vue'

const { fetchPlan, updatePlan } = useSubscriptionManager()

const props = defineProps({
  planId: { type: Number, required: true },
})

const planData = ref({})

onMounted(async () => {
  planData.value = await fetchPlan(props.planId)
})

const handleEditPlan = async (form) => {
  await updatePlan(form.plan)
}
</script>

<template>
  <DetailsCard label="Edit Plan" :data="{plan: planData}" :onSubmit="handleEditPlan" :disabledFields="['userPlan']" />
</template>
