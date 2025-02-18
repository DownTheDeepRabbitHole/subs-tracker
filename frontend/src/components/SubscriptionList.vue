<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import { RouterLink } from 'vue-router'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import DatePicker from 'primevue/datepicker'
import Dialog from 'primevue/dialog'

const toast = useToast()

const subscriptions = ref([])
const categories = ref([])
const plans = ref([])
const filters = ref({ category: '', costRange: [0, 1000], period: '' })

// Dialog & Date
const showDateDialog = ref(false)
const selectedPlan = ref(null)
const nextPaymentDate = ref(null)

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
const addToUserPlans = async () => {
  try {
    if (!nextPaymentDate.value) {
      showToast('error', 'Please select a next payment date')
      return
    }

    await axios.post('/api/user-plans/', {
      plan_id: selectedPlan.value.id,
      next_payment_date: nextPaymentDate.value.toISOString().split('T')[0], // convert to YYYY-MM-DD format
    })
    showToast('success', 'Successfully added to list')

    // Reset state
    showDateDialog.value = false
    nextPaymentDate.value = null
    selectedPlan.value = null
  } catch (error) {
    console.error('Error adding subscription:', error)
    showToast('error', "Couldn't add to list", error.response?.data?.error)
  }
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
    <div class="mb-11">
      <RouterLink to="/new-plan" icon="pi pi-plus" class="p-button-success px-3 py-2 rounded-md"> Add Plan </RouterLink>
    </div>

    <DataTable
      :value="plans"
      rowGroupMode="subheader"
      groupRowsBy="subscription"
      sortMode="single"
      sortField="subscription"
      :sortOrder="1"
      tableStyle="min-width: 50rem"
    >
      <Column field="subscription" header="Subscription" />
      <Column field="name" header="Name" style="min-width: 200px" sortable />
      <Column field="cost" header="Cost" style="min-width: 200px" sortable />
      <Column field="period" header="Period" style="min-width: 200px" />
      <Column header="Actions">
        <template #body="{ data }">
          <Button
            icon="pi pi-plus"
            @click="
              () => {
                selectedPlan = data
                showDateDialog = true
              }
            "
          />
        </template>
      </Column>

      <template #groupheader="slotProps">
        <div class="flex items-center gap-2">
          <b>{{ getSubscriptionName(slotProps.data.subscription) }}</b> - <b>{{ getCategoryName(slotProps.data.subscription) }}</b>
        </div>
      </template>
    </DataTable>

    <!-- DatePicker Dialog -->
    <Dialog header="Select Next Payment Date" v-model:visible="showDateDialog" :modal="true" :closable="false" :style="{ width: '30vw' }">
      <DatePicker v-model="nextPaymentDate" dateFormat="yy-mm-dd" showIcon />
      <div class="flex justify-end gap-2 mt-4">
        <Button label="Cancel" icon="pi pi-times" @click="showDateDialog = false" class="p-button-text" />
        <Button label="Add" icon="pi pi-check" @click="addToUserPlans" />
      </div>
    </Dialog>
  </div>
</template>
