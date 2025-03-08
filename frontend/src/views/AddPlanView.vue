<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import { useToast } from 'primevue/usetoast'

const toast = useToast()

const subscriptions = ref([])
const categories = ref([])
const periodOptions = ref(['Day', 'Week', 'Month', 'Quarter', 'Year'])
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
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Please provide all fields.',
      life: 3000,
    })
    return
  }

  try {
    console.log(newSubscription.value)
    const response = await axios.post('/api/subscriptions/', {
      name: newSubscription.value.name,
      category: newSubscription.value.category,
    })

    subscriptions.value.push(response.data)
    newPlan.value.subscription = response.data

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Subscription added.',
      life: 3000,
    })
    showDialog.value = false
  } catch (error) {
    console.error('Error adding subscription:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to add subscription.',
      life: 3000,
    })
  }
}

const createPlan = async () => {
  const { name, cost, period, subscription } = newPlan.value
  if (!name || !cost || !period || !subscription) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Please provide all required fields.',
      life: 3000,
    })
    return
  }

  try {
    await axios.post('/api/plans/', {
      name,
      cost,
      period: period.toLowerCase(),
      subscription: subscription.id,
    })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Plan created successfully.',
      life: 3000,
    })

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
      <template #content>
        <h2 class="text-xl font-semibold mb-4">Add New Plan</h2>
        <div class="p-fluid">
          <div
            class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey"
          >
            <label class="mr-3">Subscription</label>
            <AutoComplete
              v-model="newPlan.subscription"
              optionLabel="name"
              :suggestions="filteredSubs"
              @complete="searchSubscriptions"
              placeholder="Enter or select a subscription"
              class="flex-grow text-right border-none dark:bg-dark md:dark:bg-dark-grey"
            />
            <Button icon="pi pi-plus" class="p-button-text" @click="showDialog = true" />
          </div>

          <div
            class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey"
          >
            <label class="mr-3">Plan Name</label>
            <InputText
              v-model="newPlan.name"
              placeholder="Enter plan name"
              class="flex-grow text-right border-none dark:bg-dark md:dark:bg-dark-grey"
            />
          </div>

          <div
            class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey"
          >
            <label class="mr-3">Cost</label>
            <InputNumber
              v-model="newPlan.cost"
              placeholder="Enter plan cost"
              mode="currency"
              currency="CAD"
              class="dark:bg-dark md:dark:bg-dark-grey"
              :inputStyle="{ textAlign: 'right' }"
              inputClass="!border-none"
              fluid
            />
          </div>

          <div
            class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey"
          >
            <label class="mr-3">Period</label>
            <Select
              v-model="newPlan.period"
              :options="periodOptions"
              placeholder="Select period"
              class="flex-grow text-right border-none dark:bg-dark md:dark:bg-dark-grey"
            />
          </div>

          <Button label="Create Plan" class="p-button-primary w-full mt-4" @click="createPlan" />
        </div>
      </template>
    </Card>
  </div>

  <Dialog v-model:visible="showDialog" header="Add New Subscription" modal :closable="true">
    <div class="p-fluid">
      <div class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey">
        <label class="mr-3">Subscription Name</label>
        <InputText
          v-model="newSubscription.name"
          class="flex-grow text-right border-none dark:bg-dark md:dark:bg-dark-grey"
        />
      </div>
      <div class="flex items-center justify-between pt-4 pb-2 border-b-2 dark:border-medium-grey">
        <label class="mr-3">Category</label>
        <Select
          v-model="newSubscription.category"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          placeholder="Select a category"
          class="flex-grow text-right border-none dark:bg-dark md:dark:bg-dark-grey"
        />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" text @click="showDialog = false" />
      <Button
        label="Submit"
        icon="pi pi-check"
        class="p-button-primary"
        @click="addNewSubscription"
      />
    </template>
  </Dialog>
</template>
