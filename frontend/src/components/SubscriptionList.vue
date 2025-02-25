<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import { RouterLink } from 'vue-router'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import DataView from 'primevue/dataview'
import Dialog from 'primevue/dialog'
import DatePicker from 'primevue/datepicker'
import Card from './Card.vue'

const toast = useToast()

const subscriptions = ref([])
const categories = ref([])
const layout = ref('grid')
const showDateDialog = ref(false)
const selectedPlan = ref(null)
const nextPaymentDate = ref(null)

const fetchSubscriptions = async () => {
  try {
    const response = await axios.get('/api/subscriptions/')

    subscriptions.value = response.data
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}
const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')

    categories.value = response.data
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

const addToUserPlans = async () => {
  try {
    if (!nextPaymentDate.value) {
      showToast('error', 'Please select a next payment date')
      return
    }

    await axios.post('/api/user-plans/', {
      plan_id: selectedPlan.value.id,
      payment_date: nextPaymentDate.value.toISOString().split('T')[0],
    })
    showToast('success', 'Successfully added to list')

    showDateDialog.value = false
    nextPaymentDate.value = null
    selectedPlan.value = null
  } catch (error) {
    console.error('Error adding plan:', error)
    showToast('error', "Couldn't add to list", error.response?.data?.error)
  }
}

const getCategoryName = (categoryId) => {
  const category = categories.value.find((cat) => cat.id === categoryId)
  return category ? category.name : 'Unknown'
}

const showToast = (severity, summary, detail) => {
  toast.add({ severity, summary, detail, life: 3000 })
}

onMounted(() => {
  fetchCategories()
  fetchSubscriptions()
})
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <RouterLink to="/new-plan" class="p-button p-button-success">Add Plan</RouterLink>
      <Button @click="layout = layout == `grid` ? `list` : `grid`">Layout</Button>
    </div>

    <DataView :value="subscriptions" :layout="layout">
      <template #list="slotProps">
        <div class="grid grid-nogutter">
          <div v-for="(item, index) in slotProps.items" :key="index" class="col-12">
            <div class="p-3 border-b">
              <div class="mb-2">
                <b>{{ item.name }}</b> - {{ getCategoryName(item.category) }}
              </div>
              <div
                v-for="plan in item.plans"
                :key="plan.id"
                class="flex justify-between items-center ml-4 mt-2"
              >
                <span>{{ plan.name }} ({{ plan.period }}) - ${{ plan.cost }}</span>
                <Button
                  icon="pi pi-plus"
                  severity="success"
                  @click="
                    () => {
                      selectedPlan = plan
                      showDateDialog = true
                    }
                  "
                />
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #grid="slotProps">
        <div class="grid grid-cols-12 gap-4">
          <div
            v-for="(item, index) in slotProps.items"
            :key="index"
            class="col-span-12 sm:col-span-6 md:col-span-4 xl:col-span-6 p-2"
          >
            <Card>
              <div class="flex items-center space-x-2">
                <img :src="item.icon_url" alt="item.name" class="w-10 rounded-full" />
                <div>
                  <b>{{ item.name }}</b>
                  <p class="text-sm text-medium-grey">{{ getCategoryName(item.category) }}</p>
                </div>
              </div>
              <ul class="mt-2">
                <li
                  v-for="plan in item.plans"
                  :key="plan.id"
                  class="flex justify-between items-center"
                >
                  <span>{{ plan.name }} (${{ plan.cost }} / {{ plan.period }})</span>
                  <Button
                    icon="pi pi-plus"
                    severity="success"
                    @click="
                      () => {
                        selectedPlan = plan
                        showDateDialog = true
                      }
                    "
                  />
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </template>
    </DataView>

    <Dialog
      header="Select Next Payment Date"
      v-model:visible="showDateDialog"
      :modal="true"
      :closable="false"
      :style="{ width: '30vw' }"
    >
      <DatePicker v-model="nextPaymentDate" dateFormat="yy-mm-dd" showIcon />
      <div class="flex justify-end gap-2 mt-4">
        <Button
          label="Cancel"
          icon="pi pi-times"
          @click="showDateDialog = false"
          class="p-button-text"
        />
        <Button label="Add" icon="pi pi-check" @click="addToUserPlans" />
      </div>
    </Dialog>
  </div>
</template>
