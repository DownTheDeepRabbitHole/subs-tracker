<template>
  <CardWrapper title="Spending Breakdown">
    <!-- Main layout: Chart on top, details below  -->
    <div class="flex flex-col gap-8 mt-4 items-start">
      <!-- Donut Chart Wrapper (relative) -->
      <div class="relative mx-auto w-full">
        <!-- Actual ApexCharts Donut -->
        <apexchart
          type="donut"
          :options="apexOptions"
          :series="apexSeries"
          width="100%"
          height="350"
        />

        <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <div class="pointer-events-auto flex flex-col items-center text-center">
            <div class="text-4xl font-bold">
              {{ centerValue }}
            </div>

            <!-- Small sublabel (e.g. "Monthly Average") -->
            <div class="text-sm text-gray-500 mb-3">
              {{ centerSubtitle }}
            </div>

            <!-- Period Selector -->
            <Select
              v-model="selectedPeriod"
              :options="periodOptions"
              optionLabel="label"
              optionValue="value"
              class="mb-2"
              @change="handleUpdateChart"
            />

            <!-- Display Type Selector (Total vs Average) -->
            <Select
              v-model="selectedDisplayType"
              :options="displayTypeOptions"
              optionLabel="label"
              optionValue="value"
              @change="handleUpdateChart"
            />
          </div>
        </div>
      </div>

      <!-- Detail / List Section -->
      <div class="flex-1 w-full">
        <!-- If Total is selected, show the recent payments list -->
        <div v-if="isTotal" class="mb-4">
          <h2 class="mb-2">Recent Payments</h2>
          <UserPlanList
            :userPlans="recentUserPlans"
            :categories="categories"
            :fields="['plan', 'category', 'payment_date', 'cost']"
            :showFilters="false"
            :showHeaders="false"
            :paginator="false"
            @refresh="fetchRecentUserPlans"
            class="w-full"
          />
        </div>

        <!-- If Average is selected, show a category breakdown table -->
        <div v-else>
          <CategoryTable :categories="categoryBreakdown" />
        </div>
      </div>
    </div>
  </CardWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

import UserPlanList from '@/components/UserPlanList.vue'
import CardWrapper from './CardWrapper.vue'
import CategoryTable from './CategoryTable.vue'

import { useSubscriptionManager, useHelpers } from '@/composables'

const { categories, fetchUserPlans, fetchCategories } = useSubscriptionManager()
const { formatCurrency } = useHelpers()

const selectedDisplayType = ref('total') // 'total' or 'average'
const selectedPeriod = ref('month')
const spendingByCategory = ref({})
const totalOrAverageSpending = ref({})
const categoryBreakdown = ref([])
const recentUserPlans = ref([])

const apexSeries = ref([])
const apexOptions = ref({})

const displayTypeOptions = [
  { label: 'Total', value: 'total' },
  { label: 'Average', value: 'average' },
]
const periodOptions = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Year', value: 'year' },
]

const isTotal = computed(() => selectedDisplayType.value === 'total')

const centerValue = computed(() => {
  const periodValue = totalOrAverageSpending.value[selectedPeriod.value] || 0
  return formatCurrency(periodValue)
})

const centerSubtitle = computed(() => {
  const periodLabel = periodOptions.find((p) => p.value === selectedPeriod.value)?.label || ''
  return isTotal.value ? `${periodLabel} Total` : `${periodLabel} Average`
})

onMounted(async () => {
  await fetchRecentUserPlans()
  await fetchCategories()
  await fetchChartData()
  buildChart()
})

const handleUpdateChart = async () => {
  await fetchRecentUserPlans()
  await fetchChartData()
  buildChart()
}

const fetchChartData = async () => {
  try {
    const categoryData = await fetchSpendingByCategory()
    spendingByCategory.value = categoryData

    // Select the endpoint based on the display type
    const endpoint = isTotal.value
      ? '/api/analytics/total-spending-per-period/'
      : '/api/analytics/average-spending-per-period/'
    const { data } = await axios.get(endpoint)
    totalOrAverageSpending.value = data

    // Build the breakdown table for average mode
    buildCategoryBreakdown()
  } catch (err) {
    console.error('Error fetching chart data:', err)
  }
}

const fetchRecentUserPlans = async () => {
  recentUserPlans.value = await fetchUserPlans({
    period: selectedPeriod.value,
    recently_paid: 7,
    page_size: 5,
  })
}

const fetchSpendingByCategory = async () => {
  const { data } = await axios.get('/api/analytics/spending-by-category/')
  return data
}

const buildChart = () => {
  const period = selectedPeriod.value
  const labels = []
  const series = []

  for (const [catName, catData] of Object.entries(spendingByCategory.value)) {
    const iconLabel = catData.icon ? catData.icon : catName
    labels.push(iconLabel)
    series.push(catData.costs[period] || 0)
  }

  if (series.every((value) => value === 0)) {
    series.fill(1)
    labels.forEach((label, idx, arr) => {
      arr[idx] = label + ' (No Data)'
    })
  }

  apexSeries.value = series
  apexOptions.value = {
    chart: {
      type: 'donut',
      height: 350,
    },
    labels,
    dataLabels: {
      enabled: true,
      formatter: (val, opts) => {
        // Return only the icon from the corresponding label
        return opts.w.config.labels[opts.seriesIndex]
      },
    },
    tooltip: {
      y: {
        formatter: (val) => formatCurrency(val),
      },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '60%',
          labels: {
            show: false,
          },
        },
        expandOnClick: false,
      },
    },
    legend: {
      show: false,
    },
  }
}

// Creates corresponding category data for category table component, e.g. percentage
const buildCategoryBreakdown = () => {
  if (!spendingByCategory.value || !selectedPeriod.value) {
    return []
  }
  categoryBreakdown.value = []

  for (const [catName, catData] of Object.entries(spendingByCategory.value)) {
    const catCost = catData.costs[selectedPeriod.value] || 0
    const percentage = catData.percentages[selectedPeriod.value] || 0

    categoryBreakdown.value.push({
      name: catName,
      percentage,
      cost: catCost,
      icon: catData.icon || '📊',
    })
  }
}
</script>
