<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Chart from 'primevue/chart'
import Card from 'primevue/card'

const spendingByCategoryChartData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726', '#26C6DA', '#7E57C2', '#EC407A'],
    },
  ],
})
const spendingPerPeriod = ref({
  past_week: 0,
  past_month: 0,
  past_year: 0,
})
const usageByCategoryChartData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726', '#26C6DA', '#7E57C2', '#EC407A'],
    },
  ],
})

const fetchSpendingPerPeriod = async () => {
  try {
    const response = await axios.get('/api/analytics/total-spending-per-period/')
    const data = response.data
    spendingPerPeriod.value = {
      past_week: data.past_week,
      past_month: data.past_month,
      past_year: data.past_year,
    }
  } catch (error) {
    console.error('Error fetching spending per period:', error)
  }
}

const fetchUsageByCategory = async () => {
  try {
    const response = await axios.get('/api/analytics/usage-by-category/')
    const data = response.data

    // Update pie chart data
    usageByCategoryChartData.value.labels = Object.keys(data)
    usageByCategoryChartData.value.datasets[0].data = Object.values(data)
  } catch (error) {
    console.error('Error fetching usage by category:', error)
  }
}

const fetchSpendingByCategory = async () => {
  try {
    const response = await axios.get('/api/analytics/spending-by-category/')
    const data = response.data

    // Update pie chart data
    spendingByCategoryChartData.value.labels = Object.keys(data)
    spendingByCategoryChartData.value.datasets[0].data = Object.values(data).map(
      (category) => category.yearly,
    )
  } catch (error) {
    console.error('Error fetching spending by category:', error)
  }
}

// Fetch data when the component is mounted
onMounted(() => {
  fetchSpendingByCategory()
  fetchSpendingPerPeriod()
  fetchUsageByCategory()
})
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
    <!-- Spending per Period (Big Numbers) -->
    <div class="p-col-12 p-md-4">
      <Card>
        <template #content>
          <h3>Weekly Spending</h3>
          <h1 class="big-number">${{ spendingPerPeriod.past_week }}</h1>
        </template>
      </Card>
    </div>
    <div class="p-col-12 p-md-4">
      <Card>
        <template #content>
          <h3>Monthly Spending</h3>
          <h1 class="big-number">${{ spendingPerPeriod.past_month }}</h1>
        </template>
      </Card>
    </div>
    <div class="p-col-12 p-md-4">
      <Card>
      <template #content>
          <h3>Yearly Spending</h3>
          <h1 class="big-number">${{ spendingPerPeriod.past_year }}</h1>
        </template>
      </Card>
    </div>

    <!-- Spending by Category (Pie Chart) -->
    <div class="p-col-12 p-md-6">
      <Card>
      <template #content>
          <h3>Spending by Category</h3>
          <Chart type="doughnut" :data="spendingByCategoryChartData" />
        </template>
      </Card>
    </div>

    <!-- Usage by Category (Pie Chart) -->
    <div class="p-col-12">
      <Card>
        <template #content>
          <h3>Usage by Category</h3>
          <Chart type="pie" :data="usageByCategoryChartData" />
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.big-number {
  font-size: 3rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 1rem 0;
}
</style>
