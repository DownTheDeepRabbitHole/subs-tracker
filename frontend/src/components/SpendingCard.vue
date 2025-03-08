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
              @change="handlePeriodChange"
            />

            <!-- Display Type Selector (Total vs Average) -->
            <Select
              v-model="selectedDisplayType"
              :options="displayTypeOptions"
              optionLabel="label"
              optionValue="value"
              @change="updateChart"
            />
          </div>
        </div>
      </div>

      <!-- Detail / List Section -->
      <div class="flex-1 w-full">
        <!-- If Total is selected, show the recent payments list -->
        <div v-if="isTotal" class="mb-4">
          <h3 class="text-lg font-semibold mb-2">Recent Payments</h3>
          <UserPlanList
            :userPlans="userPlans"
            :categories="categories"
            :fields="['plan', 'category', 'payment_date', 'cost']"
            :showFilters="false"
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

import { useSubscriptionManager } from '@/composables/useSubscriptionManager'
import { useFormatting } from '@/composables/useFormatting'

const { formatCurrency } = useFormatting()

const selectedDisplayType = ref('total') // 'total' or 'average'
const selectedPeriod = ref('month')
const spendingByCategory = ref({})
const totalOrAverageSpending = ref({})
const categoryBreakdown = ref({})

// Chart reactivity
const apexSeries = ref([])
const apexOptions = ref({})

// Selector option arrays
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

const { userPlans, categories, fetchUserPlans, fetchCategories } = useSubscriptionManager()

onMounted(async () => {
  await fetchUserPlans()
  await fetchCategories()
  await fetchChartData()
  updateChart()
})

// Handle period changes
const handlePeriodChange = async () => {
  await fetchUserPlans({ period: selectedPeriod.value })
  await fetchChartData()
  updateChart()
}

// Fetch chart-related data from the API endpoints
const fetchChartData = async () => {
  try {
    // Fetch category-level spending data
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

// Fetch spending by category
const fetchSpendingByCategory = async () => {
  const { data } = await axios.get('/api/analytics/spending-by-category/')
  return data
}

// Build and update the ApexChart configuration
const buildApexChart = () => {
  const period = selectedPeriod.value
  const labels = []
  const series = []

  // Populate the labels and series arrays.
  // For labels, use only the icon if available (or fallback to category name)
  for (const [catName, catData] of Object.entries(spendingByCategory.value)) {
    const iconLabel = catData.icon ? catData.icon : catName
    labels.push(iconLabel)
    series.push(catData.costs[period] || 0)
  }

  // If there is no data, add dummy values with a "(No Data)" suffix
  if (series.every((value) => value === 0)) {
    series.fill(1)
    labels.forEach((label, idx, arr) => {
      arr[idx] = label + ' (No Data)'
    })
  }

  // Update the reactive chart data
  apexSeries.value = series
  apexOptions.value = {
    chart: {
      type: 'donut',
      height: 350,
    },
    labels, // The labels now contain just the icon for each category
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

// Build category breakdown data for display (used in average mode)
const buildCategoryBreakdown = () => {
  categoryBreakdown.value = {}
  const period = selectedPeriod.value

  // Calculate the total cost across all categories
  let totalCost = 0
  for (const catData of Object.values(spendingByCategory.value)) {
    totalCost += catData[period] || 0
  }

  // Compute each category's cost and percentage share
  for (const [catName, catData] of Object.entries(spendingByCategory.value)) {
    const catCost = catData.costs[period] || 0
    const percentage = catData.percentages[period] || 0
    categoryBreakdown.value[catName] = {
      cost: catCost,
      percentage,
      icon: catData.icon,
    }
  }
}

// Update the chart whenever the display type changes
const updateChart = () => {
  buildApexChart()
}
</script>
