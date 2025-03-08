<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

import StatsCard from '@/components/StatsCard.vue'
import ChartCard from '@/components/ChartCard.vue'
import SpendingCard from '@/components/SpendingCard.vue'

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
      (category) => category.year,
    )
  } catch (error) {
    console.error('Error fetching spending by category:', error)
  }
}

// Computed properties to check if the chart data is non-zero
const hasSpendingByCategoryData = computed(() => {
  return spendingByCategoryChartData.value.datasets[0].data.some((value) => value > 0)
})

const hasUsageByCategoryData = computed(() => {
  return usageByCategoryChartData.value.datasets[0].data.some((value) => value > 0)
})

// Fetch data when the component is mounted
onMounted(() => {
  fetchSpendingByCategory()
  fetchSpendingPerPeriod()
  fetchUsageByCategory()
})
</script>

<template>
  <div class="grid grid-flow-dense grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Spending Cards -->
    <StatsCard title="Weekly Spending" :amount="spendingPerPeriod.past_week" />
    <StatsCard title="Monthly Spending" :amount="spendingPerPeriod.past_month" />
    <StatsCard title="Yearly Spending" :amount="spendingPerPeriod.past_year" />

    <!-- Conditional rendering for Spending by Category chart -->
    <ChartCard
      v-if="hasSpendingByCategoryData"
      title="Spending by Category"
      chartType="doughnut"
      :chartData="spendingByCategoryChartData"
    />

    <!-- Conditional rendering for Usage by Category chart -->
    <ChartCard
      v-if="hasUsageByCategoryData"
      title="Usage by Category"
      chartType="pie"
      :chartData="usageByCategoryChartData"
    />

    
  </div>
  <SpendingCard/>
</template>
