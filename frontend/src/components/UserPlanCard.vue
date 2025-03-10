<script setup>
import { computed } from 'vue'
import axios from 'axios'

import { useSubscriptionManager } from '@/composables'

import { formatDistanceToNow } from 'date-fns'

const { deleteUserPlan, toggleUsage } = useSubscriptionManager()

const props = defineProps({
  userPlan: {
    type: Object,
    required: true,
    default: () => {},
  },
})

const emit = defineEmits(['refresh'])

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

const handleDeleteUserPlan = async () => {
  await deleteUserPlan(props.userPlan['id'])
  emit('refresh')
}

const handleToggleUsage = async () => {
  await toggleUsage(props.userPlan['id'], props.userPlan['track_usage'])
  props.userPlan['track_usage'] = !props.userPlan['track_usage']
}
</script>

<template>
  <Card class="hover:shadow-lg transition-shadow duration-200">
    <template #header>
      <div class="flex items-center gap-4 p-4 border-b border-gray-300">
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
      <div class="flex justify-end gap-2 p-4 border-t border-gray-300">
        <Button
          icon="pi pi-trash"
          severity="danger"
          outlined
          rounded
          @click="handleDeleteUserPlan"
          aria-label="Delete plan"
        />
        <Button
          :icon="userPlan.track_usage ? 'pi pi-chart-line' : 'pi pi-eye-slash'"
          :severity="userPlan.track_usage ? 'success' : 'secondary'"
          outlined
          rounded
          @click="handleToggleUsage"
          :aria-label="`${userPlan.track_usage ? 'Disable' : 'Enable'} usage tracking`"
        />
      </div>
    </template>
  </Card>
</template>
