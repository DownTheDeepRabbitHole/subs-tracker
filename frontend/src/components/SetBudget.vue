<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

import { useToast } from 'primevue'

import UserPlanList from './UserPlanList.vue'
import UserPlanCard from './UserPlanCard.vue'
import CardWrapper from './CardWrapper.vue'

const toast = useToast()

const categories = ref([])
const selectedCategory = ref(null)
const budgetInput = ref('')
const userPlans = ref([])
const budgetApplied = ref(false)

// Computed property to determine if all subscriptions fit in budget
const allWithinBudget = computed(() => {
  return budgetApplied.value && userPlans.value.length === 0
})

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')
    categories.value = response.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

// Handler to call the set budget API
const handleSetBudget = async () => {
  if (!budgetInput.value) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter a budget.', life: 3000 })
    return
  }
  try {
    budgetApplied.value = false // Reset before making request
    const response = await axios.get('/api/analytics/set-budget/', {
      params: {
        budget: budgetInput.value,
        ...(selectedCategory.value?.id && { category_id: selectedCategory.value.id }),
      },
    })
    userPlans.value = response.data.subscriptions
    budgetApplied.value = true // Set flag indicating budget was applied

    // Show success message
    const categoryText = selectedCategory.value ? `for ${selectedCategory.value.name}` : ''
    toast.add({
      severity: 'success',
      summary: 'Budget Applied',
      detail: `Budget of $${budgetInput.value} has been set ${categoryText}`,
      life: 3000,
    })

    console.log(userPlans.value)
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
      <input
        v-model="budgetInput"
        type="number"
        placeholder="Enter your budget"
        class="border border-gray-300 rounded px-3 py-2 w-full md:w-1/3"
      />
      <Select
        v-model="selectedCategory"
        :options="categories"
        optionLabel="name"
        placeholder="Select Category"
        class="w-full md:w-1/3"
        showClear
      />
      <!-- Set Budget Button -->
      <Button label="Set Budget" @click="handleSetBudget" class="w-full md:w-auto" />
    </div>
  </CardWrapper>

  <!-- Budget Results -->
  <div v-if="budgetApplied" class="mt-6">
    <!-- Show success message when all subscriptions fit within budget -->
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

    <!-- Display User Plans that exceed the budget -->
    <div v-else class="space-y-4">
      <h2 class="text-xl font-semibold">Subscriptions Exceeding Budget</h2>
      <p class="text-gray-600">
        Consider reducing or canceling these subscriptions to stay within budget.
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Corrected reference to 'userPlans' (lowercase 'u') -->
        <UserPlanCard
          v-for="userPlan in userPlans"
          :key="userPlan.id"
          :userPlan="userPlan"
          @refresh="handleSetBudget"
        />
      </div>
    </div>
  </div>
</template>
