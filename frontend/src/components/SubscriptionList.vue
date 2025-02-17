<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import { useToast } from 'primevue/usetoast'

import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const toast = useToast()

const subscriptions = ref([])
const categories = ref([])
const plans = ref([])
const filters = ref({ category: '', costRange: [0, 1000], period: '' })
const periodOptions = ref(['Day', 'Month', 'Quarter', 'Year'])

const showDialog = ref(false)
const newPlan = ref({ name: '', cost: 0, period: '', subscription: null, newSubscription: { name: '', category: null } })

// Fetch Data
const fetchData = async (endpoint, refValue) => {
  try {
    const response = await axios.get(`/api/${endpoint}/`)
    refValue.value = response.data
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error)
  }
}

const fetchPlans = async () => {
  try {
    const { category, costRange, period } = filters.value
    if (costRange[0] > costRange[1]) filters.value.costRange = [costRange[1], costRange[0]]

    const queryParams = new URLSearchParams({
      cost_min: costRange[0],
      cost_max: costRange[1],
      ...(category && { category_id: category }),
      ...(period && { period: period.toLowerCase() }),
    }).toString()

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

// Actions
const addToUserPlans = async (planId) => {
  try {
    await axios.post('/api/user-plans/', { plan_id: planId })
    showToast('success', 'Successfully added to list')
  } catch (error) {
    console.error('Error adding subscription:', error)
    showToast('error', "Couldn't add to list", error.response?.data?.error)
  }
}

const createSubscription = async () => {
  const { name, category } = newPlan.value.newSubscription
  if (!name || !category) {
    showToast('error', 'Invalid Data', 'Please provide all required fields for the new subscription.')
    return
  }

  try {
    const response = await axios.post('/api/subscriptions/', { name, category })
    newPlan.value.subscription = response.data.id
    showToast('success', 'New Subscription Created', 'The new subscription has been added successfully.')
  } catch (error) {
    console.error('Error creating subscription:', error)
    showToast('error', 'Error', 'Failed to create subscription.')
  }
}

const createPlan = async () => {
  const { name, cost, period, subscription } = newPlan.value
  if (!name || !cost || !period || !subscription) {
    showToast('error', 'Invalid Data', 'Please provide all required fields for the plan.')
    return
  }

  try {
    await axios.post('/api/plans/', { name, cost, period, subscription })
    showToast('success', 'Plan Created', 'The plan has been created successfully.')
    showDialog.value = false
    resetNewPlan()
    fetchPlans()
  } catch (error) {
    console.error('Error creating plan:', error)
    showToast('error', 'Error', 'Failed to create plan.')
  }
}

const resetNewPlan = () => {
  newPlan.value = { name: '', cost: 0, period: '', subscription: null, newSubscription: { name: '', category: null } }
}

const showToast = (severity, summary, detail) => {
  toast.add({ severity, summary, detail, life: 3000 })
}

onMounted(() => {
  fetchData('categories', categories)
  fetchData('subscriptions', subscriptions)
  fetchPlans()
})
</script>

<template>
  <div>
    <Button label="Create Plan" icon="pi pi-plus" class="p-button-success mb-4" @click="showDialog = true" />

    <Dialog v-model:visible="showDialog" header="Create Plan" modal>
      <div class="p-fluid">
        <div class="field">
          <label for="subscription">Subscription</label>
          <Dropdown
            id="subscription"
            v-model="newPlan.subscription"
            :options="subscriptions"
            optionLabel="name"
            optionValue="id"
            placeholder="Select an existing subscription"
          />
          <Button v-if="!newPlan.subscription" label="Add New Subscription" icon="pi pi-plus" class="p-button-text" @click="createSubscription" />
        </div>

        <template v-if="!newPlan.subscription">
          <div class="field">
            <label for="new-subscription-name">New Subscription Name</label>
            <InputText v-model="newPlan.newSubscription.name" placeholder="Enter new subscription name" />
          </div>
          <div class="field">
            <label for="new-subscription-category">Category</label>
            <Dropdown
              id="new-subscription-category"
              v-model="newPlan.newSubscription.category"
              :options="categories"
              optionLabel="name"
              optionValue="id"
              placeholder="Select a category"
            />
          </div>
        </template>

        <div class="field">
          <label for="plan-name">Plan Name</label>
          <InputText v-model="newPlan.name" id="plan-name" placeholder="Enter plan name" />
        </div>
        <div class="field">
          <label for="plan-cost">Cost</label>
          <InputText v-model="newPlan.cost" id="plan-cost" type="number" placeholder="Enter plan cost" />
        </div>
        <div class="field">
          <label for="plan-period">Period</label>
          <Dropdown v-model="newPlan.period" :options="periodOptions" placeholder="Select period" />
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showDialog = false" />
        <Button label="Create Plan" icon="pi pi-check" class="p-button-primary" @click="createPlan" />
      </div>
    </Dialog>

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
      <Column field="subscription" header="Subscription" />
      <Column field="name" header="Name" style="min-width: 200px" sortable />
      <Column field="cost" header="Cost" style="min-width: 200px" sortable />
      <Column field="period" header="Period" style="min-width: 200px" />
      <Column header="Actions">
        <template #body="{ data }">
          <Button icon="pi pi-plus" @click="addToUserPlans(data.id)" />
        </template>
      </Column>

      <template #groupheader="slotProps">
        <div class="flex items-center gap-2">
          <b>{{ getSubscriptionName(slotProps.data.subscription) }}</b> - <b>{{ getCategoryName(slotProps.data.subscription) }}</b>
        </div>
      </template>
    </DataTable>
  </div>
</template>
