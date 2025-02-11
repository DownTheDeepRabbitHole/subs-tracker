<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import Filters from './Filters.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'

const toast = useToast()

// Data
const subscriptions = ref([])
const categories = ref([])
const plans = ref([])
const filters = ref({
  category: '',
  costRange: [0, 1000],
  period: '',
})

const periodOptions = ref(['Day', 'Month', 'Quarter', 'Year'])

// Fetch Categories
const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')
    categories.value = response.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

// Fetch Subscriptions
const fetchSubscriptions = async () => {
  try {
    const response = await axios.get('/api/subscriptions/')
    subscriptions.value = response.data
  } catch (error) {
    console.error('Error fetching subscriptions:', error)
  }
}

// Fetch Plans with applied filters
const fetchPlans = async () => {
  try {
    const { category, costRange, period } = filters.value

    if (costRange[0] > costRange[1]) filters.value.costRange = [costRange[1], costRange[0]]

    let queryParams = ''

    queryParams += `cost_min=${costRange[0]}&`
    queryParams += `cost_max=${costRange[1]}&`
    if (category) queryParams += `category_id=${category}&`
    if (period) queryParams += `period=${period.toLowerCase()}&`

    queryParams = queryParams ? queryParams.slice(0, -1) : '' // Remove trailing "&"

    const response = await axios.get(`/api/plans/?${queryParams}`)
    plans.value = response.data
  } catch (error) {
    console.error('Error fetching plans:', error)
  }
}

// Helper function to get the category name by ID
const getCategoryName = (categoryId) => {
  const category = categories.value.find((cat) => cat.id === categoryId)
  return category ? category.name : 'Unknown'
}

// Helper function to get the subscription name by ID
const getSubscriptionName = (subscriptionId) => {
  const subscription = subscriptions.value.find((sub) => sub.id === subscriptionId)
  return subscription ? subscription.name : 'Unknown'
}

// Add plan to user plans
const addToUserPlans = async (planId) => {
  try {
    await axios.post('/api/user-plans/', { plan_id: planId })
    showSuccess('Successfully added to list')
  } catch (error) {
    console.error('Error adding subscription:', error)
    showError("Couldn't add to list", error.response.data['error'])
  }
}

onMounted(() => {
  fetchCategories()
  fetchSubscriptions()
  fetchPlans()
})

const showSuccess = (message, content) => {
  toast.add({ severity: 'success', summary: message, detail: content, life: 3000 })
}

const showError = (message, content) => {
  toast.add({ severity: 'error', summary: message, detail: content, life: 3000 })
}
</script>

<template>
  <div>
    <!-- Filter Component -->
    <Filters :categories="categories" :periodOptions="periodOptions" :filters="filters" @filter-change="fetchPlans" />

    <!-- Subscription DataTable -->
    <DataTable
      :value="plans"
      rowGroupMode="subheader"
      groupRowsBy="subscription"
      sortMode="single"
      sortField="subscription"
      :sortOrder="1"
      scrollable
      scrollHeight="400px"
      tableStyle="min-width: 50rem"
    >
      <Column field="subscription" header="Subscription"></Column>
      <Column field="name" header="Name" style="min-width: 200px" sortable></Column>
      <Column field="cost" header="Cost" style="min-width: 200px" sortable></Column>
      <Column field="period" header="Period" style="min-width: 200px"></Column>
      <Column header="Actions">
        <template #body="{ data }">
          <Button icon="pi pi-plus" @click="addToUserPlans(data.id)" />
        </template>
      </Column>

      <template #groupheader="slotProps">
        <div class="flex items-center gap-2">
          <b>{{ getSubscriptionName(slotProps.data.subscription) }}</b> -
          <b>{{ getCategoryName(slotProps.data.subscription) }}</b>
        </div>
      </template>
    </DataTable>
  </div>
</template>
