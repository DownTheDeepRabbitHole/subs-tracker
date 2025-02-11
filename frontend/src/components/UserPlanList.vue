<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Filters from './Filters.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const categories = ref([])
const userPlans = ref([])
const filters = ref({
  category: '',
  costRange: [0, 1000],
  period: '',
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
    const response = await axios.get('/api/user-plans/')
    userPlans.value = response.data
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
    <Filters :categories="categories" :periodOptions="periodOptions" :filters="filters" @filter-change="fetchUserPlans" />
    <DataTable :value="userPlans">
      <Column field="plan.subscription.name" header="Name">
        <template #body="slotProps"> {{ slotProps.data.plan.subscription.name }} - {{ slotProps.data.plan.name }} </template>
      </Column>
      <Column field="plan.subscription.category" header="Category">
        <template #body="slotProps">
          {{ getCategoryName(slotProps.data.plan.subscription.category) }}
        </template>
      </Column>
      <Column field="plan.cost" header="Cost"></Column>
      <Column field="plan.period" header="Period"></Column>
    </DataTable>
  </div>
</template>
