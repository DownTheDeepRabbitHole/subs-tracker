<script setup>
import { computed } from 'vue'
import axios from 'axios'

import { formatDistanceToNow } from 'date-fns'

const props = defineProps({
  userPlan: {
    type: Object,
    required: true,
    default: () => {},
  },
})

const emit = defineEmits(['refresh'])

// Computed properties
const formattedPeriod = computed(() => {
  return props.userPlan.period.charAt(0).toUpperCase() + props.userPlan.period.slice(1)
})

const formattedCost = computed(() => {
  return props.userPlan.cost.toFixed(2)
})

const paymentDateStatus = computed(() => {
  const daysUntil = Math.ceil(
    (new Date(props.userPlan.payment_date) - new Date()) / (1000 * 60 * 60 * 24),
  )

  if (daysUntil <= 7) return 'text-red-500'
  if (daysUntil <= 30) return 'text-orange-500'
  return 'text-green-500'
})

const usagePercentage = computed(() => {
  return (props.userPlan.usage_score / 10) * 100
})

const usageColor = computed(() => {
  if (props.userPlan.usage_score <= 3) return 'bg-red-500'
  if (props.userPlan.usage_score <= 6) return 'bg-orange-500'
  return 'bg-green-500'
})

const deleteUserPlan = async () => {
  try {
    await axios.delete(`/api/user-plans/${props.userPlan['id']}/`)
    emit('refresh')
  } catch (error) {
    console.error('Error deleting user plan:', error)
  }
}

const toggleUsage = async () => {
  try {
    await axios.patch(`/api/user-plans/${props.userPlan['id']}/toggle-usage/`, {
      track_usage: !props.userPlan['track_usage'],
    })
    emit('refresh')
  } catch (error) {
    console.error('Error toggling track usage:', error)
  }
}
</script>

<template>
  <Card class="hover:shadow-lg transition-shadow duration-200">
    <template #header>
      <div class="flex items-center gap-4 p-4 border-b">
        <img
          :src="userPlan.icon_url"
          :alt="userPlan.subscription_name"
          class="w-12 h-12 rounded-lg object-contain"
        />
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            {{ userPlan.subscription_name }}
          </h3>
          <p class="text-sm text-gray-500">{{ userPlan.plan_name }} • {{ formattedPeriod }}</p>
        </div>
      </div>
    </template>

    <template #content>
      <div class="grid gap-4 p-4">
        <!-- Cost Section -->
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Cost</span>
          <div class="flex items-baseline gap-2">
            <span class="text-xl font-semibold text-gray-900"> ${{ formattedCost }} </span>
            <span class="text-sm text-gray-500">/{{ formattedPeriod.toLowerCase() }}</span>
          </div>
        </div>

        <!-- Payment Date -->
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Next Payment</span>
          <span :class="['text-sm font-medium', paymentDateStatus]">
            {{ formatDistanceToNow(new Date(userPlan.payment_date), { addSuffix: true }) }}
          </span>
        </div>

        <!-- Usage Tracking -->
        <div v-if="userPlan.track_usage" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Usage Score</span>
            <span class="font-medium">{{ userPlan.usage_score }}/10</span>
          </div>
          <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              :class="['h-full transition-all duration-500', usageColor]"
              :style="{ width: `${usagePercentage}%` }"
            />
          </div>
        </div>

        <div v-else class="text-center py-2 bg-gray-50 rounded">
          <span class="text-sm text-gray-500">Usage tracking disabled</span>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2 p-4 border-t">
        <Button
          icon="pi pi-trash"
          severity="danger"
          outlined
          rounded
          @click="deleteUserPlan"
          aria-label="Delete plan"
        />
        <Button
          :icon="userPlan.track_usage ? 'pi pi-chart-line' : 'pi pi-eye-slash'"
          :severity="userPlan.track_usage ? 'success' : 'secondary'"
          outlined
          rounded
          @click="toggleUsage"
          :aria-label="`${userPlan.track_usage ? 'Disable' : 'Enable'} usage tracking`"
        />
      </div>
    </template>
  </Card>
</template>

<!-- <style scoped>
.plan-card {
  @apply bg-white rounded-xl border border-gray-200;
}

:deep(.p-card-header) {
  @apply border-b border-gray-200;
}

:deep(.p-card-content) {
  @apply p-0;
}

:deep(.p-card-footer) {
  @apply border-t border-gray-200 p-0;
} -->
<!-- </style> -->
