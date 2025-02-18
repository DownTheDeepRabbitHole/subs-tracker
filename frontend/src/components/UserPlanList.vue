<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import Select from 'primevue/select'
import Slider from 'primevue/slider'
import InputNumber from 'primevue/inputnumber'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Checkbox from 'primevue/checkbox'

const categories = ref([])
const userPlans = ref([])
const filters = ref({
  category: '',
  costRange: [0, 1000],
  period: '',
  usage_score: '',
  track_usage: '',
})

const periodOptions = ref(['Day', 'Month', 'Quarter', 'Year'])

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')
    categories.value = response.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const fetchUserPlans = async () => {
  try {
    const { category, costRange, period } = filters.value
    if (costRange[0] > costRange[1]) filters.value.costRange = [costRange[1], costRange[0]]

    const queryParams = new URLSearchParams({
      cost_min: costRange[0],
      cost_max: costRange[1],
      ...(category && { category_id: category }),
      ...(period && { period: period.toLowerCase() }),
    }).toString()

    const response = await axios.get(`/api/user-plans/?${queryParams}`)
    userPlans.value = response.data
    console.log(userPlans)
  } catch (error) {
    console.error('Error fetching user plans:', error)
  }
}

onMounted(() => {
  fetchUserPlans()
  fetchCategories()
})

const getCategoryName = (categoryId) => {
  const category = categories.value.find((cat) => cat.id === categoryId)
  return category ? category.name : 'Unknown'
}
</script>

<template>
  <div>
    <!-- Filters -->
    <div class="flex justify-between items-center space-x-4 mb-6">
      <!-- Category Filter -->
      <div class="w-1/3">
        <label class="block text-sm font-semibold">Category</label>
        <Select
          id="category"
          v-model="filters.category"
          :options="categories"
          option-label="name"
          option-value="id"
          placeholder="Select Category"
          showClear
          @change="fetchUserPlans"
          fluid
        />
      </div>

      <!-- Period Filter -->
      <div class="w-1/3">
        <label class="block text-sm font-semibold">Period</label>
        <Select id="period" v-model="filters.period" :options="periodOptions" showClear placeholder="Select Period" @change="fetchUserPlans" fluid />
      </div>

      <!-- Cost Range Filters -->
      <div class="w-1/3">
        <label class="block text-sm font-semibold">Cost</label>
        <div class="flex items-center space-x-4">
          <InputNumber v-model="filters.costRange[0]" :min="0" :max="filters.costRange[1]" @input="fetchUserPlans" class="w-1/5" />
          <Slider id="costRange" v-model="filters.costRange" @change="fetchUserPlans" :min="0" :max="1000" range class="w-3/5" />
          <InputNumber v-model="filters.costRange[1]" :min="filters.costRange[0]" :max="1000" @input="fetchUserPlans" class="w-1/5" />
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <DataTable :value="userPlans" removableSort>
      <Column field="plan.subscription.name" header="Name">
        <template #body="slotProps"> {{ slotProps.data.plan.subscription.name }} - {{ slotProps.data.plan.name }} </template>
      </Column>
      <Column field="plan.subscription.category" header="Category">
        <template #body="slotProps">
          {{ getCategoryName(slotProps.data.plan.subscription.category) }}
        </template>
      </Column>
      <Column field="plan.cost" header="Cost" sortable></Column>
      <Column field="plan.period" header="Period"></Column>
      <Column field="usage_score" header="Usage Score" sortable></Column>
      <Column field="track_usage" header="Track Usage">
        <template #body="slotProps">
          <i v-if="slotProps.data.track_usage" class="pi pi-check" style="color: green"> </i>
          <i v-else class="pi pi-times" style="color: red"></i>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style>
.p-inputnumber input {
  width: 10px;
}
</style>
