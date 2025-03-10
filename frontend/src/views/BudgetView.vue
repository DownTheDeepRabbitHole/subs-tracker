<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

import { useSubscriptionManager } from '@/composables'

import { useToast } from 'primevue'

import UserPlanList from '@/components/UserPlanList.vue'
import UserPlanCard from '@/components/UserPlanCard.vue'
import CardWrapper from '@/components/CardWrapper.vue'

const { categories, fetchCategories } = useSubscriptionManager()
const toast = useToast()

const selectedCategory = ref(null)
const budgetInput = ref('')
const includedUserPlans = ref([])
const excludedUserPlans = ref([])
const budgetApplied = ref(false)

const allWithinBudget = computed(() => {
  return budgetApplied.value && excludedUserPlans.value.length === 0
})

const showUserPlanList = ref(false)
const toggleUserPlanList = () => {
  showUserPlanList.value = !showUserPlanList.value
}

const handleSetBudget = async () => {
  if (!budgetInput.value) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter a budget.', life: 3000 })
    return
  }
  try {
    budgetApplied.value = false
    const response = await axios.get('/api/analytics/set-budget/', {
      params: {
        budget: budgetInput.value,
        ...(selectedCategory.value?.id && { category_id: selectedCategory.value.id }),
      },
    })
    includedUserPlans.value = response.data.included_plans
    excludedUserPlans.value = response.data.excluded_plans
    budgetApplied.value = true

    const categoryText = selectedCategory.value ? `for ${selectedCategory.value.name}` : ''
    toast.add({
      severity: 'success',
      summary: 'Budget Applied',
      detail: `Budget of $${budgetInput.value} has been set ${categoryText}`,
      life: 3000,
    })
  } catch (error) {
    console.error('Error setting budget:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.error || 'Failed to apply budget',
      life: 3000,
    })
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <CardWrapper title="Set Your Budget">
    <div class="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0 items-center">
      <InputNumber
        v-model="budgetInput"
        mode="currency"
        currency="CAD"
        placeholder="Enter your budget"
        class="w-full md:w-3/5"
      />
      <Select
        v-model="selectedCategory"
        :options="categories"
        optionLabel="name"
        placeholder="Select Category"
        showClear
        class="w-full md:w-1/5"
      />
      <Button label="Set Budget" @click="handleSetBudget" class="w-full md:w-1/5" />
    </div>

    <div v-if="showUserPlanList" class="mt-6">
      <h2>Budgeted subscriptions</h2>
      <UserPlanList :userPlanList="includedUserPlans" :showFilters="false" />
    </div>

    <div class="flex justify-center mt-4">
      <Button
        icon="pi pi-chevron-down"
        severity="secondary"
        @click="toggleUserPlanList"
        :class="{ 'rotate-180': showUserPlanList }"
        class="w-full md:w-1/5"
      />
    </div>
  </CardWrapper>

  <div v-if="budgetApplied" class="mt-6">
    <div v-if="allWithinBudget" class="p-6 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-center">
        <i class="pi pi-check-circle text-green-500 text-2xl mr-3"></i>
        <div>
          <h3 class="text-xl font-semibold text-green-700">Great News!</h3>
          <p class="text-green-600">
            All your subscriptions fit within your budget of ${{ budgetInput }}.
            {{ selectedCategory ? `Category: ${selectedCategory.name}` : '' }}
          </p>
        </div>
      </div>
    </div>

    <div v-else class="space-y-4">
      <h2 class="text-xl font-semibold">Subscriptions Exceeding Budget</h2>
      <p class="text-gray-600">
        Consider reducing or canceling these subscriptions to stay within budget.
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UserPlanCard
          v-for="userPlan in excludedUserPlans"
          :key="userPlan.id"
          :userPlan="userPlan"
          @refresh="handleSetBudget"
        />
      </div>
    </div>
  </div>
</template>
