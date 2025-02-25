<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import { useToast } from 'primevue/usetoast'

import Card from '@/components/Card.vue'
import AutoComplete from 'primevue/autocomplete'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'

const toast = useToast()

const subscriptions = ref([])
const categories = ref([])
const periodOptions = ref(['Day', 'Month', 'Quarter', 'Year'])
const filteredSubs = ref([])
const showDialog = ref(false)

const newPlan = ref({
  name: '',
  cost: 0,
  period: '',
  subscription: null,
})

const newSubscription = ref({
  name: '',
  category: null,
})

onMounted(() => {
  fetchData('categories', categories)
  fetchData('subscriptions', subscriptions)
})

const fetchData = async (endpoint, refValue) => {
  try {
    const response = await axios.get(`/api/${endpoint}/`)
    refValue.value = response.data
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error)
  }
}

const searchSubscriptions = (event) => {
  const query = event.query.toLowerCase()
  filteredSubs.value = subscriptions.value.filter((sub) => sub.name.toLowerCase().includes(query))
}

const addNewSubscription = async () => {
  if (!newSubscription.value.name || !newSubscription.value.category) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Please provide all fields.', life: 3000 })
    return
  }

  try {
    const response = await axios.post('/api/subscriptions/', {
      name: newSubscription.value.name,
      category: newSubscription.value.category,
    })
    subscriptions.value.push(response.data)
    newPlan.value.subscription = response.data
    toast.add({ severity: 'success', summary: 'Success', detail: 'Subscription added.', life: 3000 })
    showDialog.value = false
  } catch (error) {
    console.error('Error adding subscription:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add subscription.', life: 3000 })
  }
}

const createPlan = async () => {
  const { name, cost, period, subscription } = newPlan.value
  if (!name || !cost || !period || !subscription) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Please provide all required fields.', life: 3000 })
    return
  }

  try {
    await axios.post('/api/plans/', {
      name,
      cost,
      period: period.toLowerCase(),
      subscription: subscription.id,
    })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Plan created successfully.', life: 3000 })

    newPlan.value = { name: '', cost: 0, period: '', subscription: null }
    newSubscription.value = { name: '', category: null }
  } catch (error) {
    console.error('Error creating plan:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create plan.', life: 3000 })
  }
}
</script>

<template>
  <div class="min-w-[80%] grid grid-cols-2 gap-4 p-4">
    <Card>
      <h2 class="text-xl font-semibold mb-4">Add New Plan</h2>
      <div class="p-fluid">
        <div class="field">
          <label for="subscription">Subscription</label>
          <div class="flex items-center">
            <AutoComplete
              id="subscription"
              v-model="newPlan.subscription"
              optionLabel="name"
              :suggestions="filteredSubs"
              @complete="searchSubscriptions"
              placeholder="Enter or select a subscription"
              class="w-full"
            >
              <template #footer>
                <div class="px-3 py-3">
                  <Button label="Add New" fluid severity="secondary" text size="small" icon="pi pi-plus" @click="showDialog = true" />
                </div>
              </template>
            </AutoComplete>
            <Button icon="pi pi-plus" class="p-button-text" @click="showDialog = true" />
          </div>
        </div>

        <div class="field">
          <label for="plan-name">Plan Name</label>
          <InputText v-model="newPlan.name" id="plan-name" placeholder="Enter plan name" class="w-full" />
        </div>

        <div class="field">
          <label for="plan-cost">Cost</label>
          <InputNumber v-model="newPlan.cost" id="plan-cost" mode="currency" currency="CAD" placeholder="Enter plan cost" class="w-full" />
        </div>

        <div class="field">
          <label for="plan-period">Period</label>
          <Select v-model="newPlan.period" :options="periodOptions" placeholder="Select period" class="w-full" />
        </div>

        <Button label="Create Plan" class="p-button-primary w-full mt-4" @click="createPlan" />
      </div>
    </Card>

    <Card class="flex flex-col items-center justify-center">
      <div class="bg-purple-500 text-white p-4 rounded-lg w-64 text-center">
        <h3 class="text-lg font-semibold">{{ newPlan.subscription?.name || 'Subscription' }}</h3>
        <p class="text-xl">C$ {{ newPlan.cost.toFixed(2) }}</p>
      </div>
    </Card>
  </div>

  <Dialog v-model:visible="showDialog" header="Add New Subscription" modal :closable="true">
    <div class="p-fluid">
      <div class="field">
        <label for="new-subscription-name">Subscription Name</label>
        <InputText id="new-subscription-name" v-model="newSubscription.name" class="w-full" />
      </div>
      <div class="field">
        <label for="new-subscription-category">Category</label>
        <Select
          id="new-subscription-category"
          v-model="newSubscription.category"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          placeholder="Select a category"
          class="w-full"
        />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" text @click="showDialog = false" />
      <Button label="Submit" icon="pi pi-check" class="p-button-primary" @click="addNewSubscription" />
    </template>
  </Dialog>
</template>
