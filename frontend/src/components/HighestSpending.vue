<template>
  <CardWrapper>
    <!-- Header with cost + period selector -->
    <div class="flex items-center justify-between mb-4">
      <!-- Left: total or average cost per period -->
      <div class="text-xl font-semibold flex items-center gap-2">
        <span>
          <!-- You can compute a sum of cost if you want total across all plans -->
          {{ totalCostDisplay }} per
        </span>
        <Select
          v-model="selectedPeriod"
          :options="periodOptions"
          optionLabel="label"
          optionValue="value"
          @change="fetchUserPlans({ period: selectedPeriod.value })"
        />
      </div>
    </div>

    <!-- The bar chart -->
    <div>
      <apexchart type="bar" height="400" :options="apexOptions" :series="apexSeries" />
    </div>
  </CardWrapper>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import CardWrapper from './CardWrapper.vue'

import { useSubscriptionManager } from '@/composables/useSubscriptionManager'
import { useFormatting } from '@/composables/useFormatting'

const { userPlans, fetchUserPlans } = useSubscriptionManager()
const { formatCurrency } = useFormatting()

const selectedPeriod = ref('month')

const periodOptions = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Year', value: 'year' },
]

// Chart data
const apexOptions = ref({})
const apexSeries = ref([])

/**
 * Derived total cost across all plans
 * If you only want to show a single plan's cost, remove this or adapt as needed.
 */
const totalCostDisplay = computed(() => {
  const total = userPlans.value.reduce((sum, plan) => {
    // plan.cost is annotated from your Django view if `period` is passed
    return sum + Number(plan.cost ?? 0)
  }, 0)
  return formatCurrency(total)
})

onMounted(() => {
  fetchUserPlans({ period: selectedPeriod.value })
})

function handlePeriodChange() {
  
}

/* -------------------------------------
     Chart Construction
  -------------------------------------- */
function buildChart() {
  // We'll display two bars for each subscription: cost & usage
  // The x-axis label will show an icon or name, etc.
  // If your model does not provide usage, adapt or remove usage from the series.

  const categories = userPlans.value.map((plan) => {
    // Example: plan.plan.subscription.icon or name
    const sub = plan.plan.subscription
    // If you have an icon (e.g., emoji or short text), you can combine them:
    // return `${sub.icon || ''} ${sub.name}`
    // Or just use the icon if that’s your desired label
    return sub.icon || sub.name
  })

  // Build the "cost" series data
  const costData = userPlans.value.map((plan) => Number(plan.cost ?? 0))

  // If you track usage (e.g., plan.usage) or something similar:
  const usageData = userPlans.value.map((plan) => Number(plan.usage ?? 0))

  // The series: two bars side-by-side for each category
  apexSeries.value = [
    {
      name: 'Cost',
      data: costData,
    },
    {
      name: 'Usage',
      data: usageData,
    },
  ]

  // Configure the chart
  apexOptions.value = {
    chart: {
      type: 'bar',
      stacked: false,
      toolbar: { show: false },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '50%',
        dataLabels: {
          position: 'top',
        },
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val, opts) => {
        // For the cost series, format as currency. For usage, show as is.
        if (opts.seriesIndex === 0) {
          return formatCurrency(val)
        } else {
          return val // or `${val} units`, etc.
        }
      },
      offsetY: -20,
      style: {
        fontSize: '12px',
        colors: ['#333'],
      },
    },
    xaxis: {
      categories,
      labels: {
        style: {
          fontSize: '14px',
        },
      },
    },
    yaxis: [
      {
        // Left Y-axis for cost
        labels: {
          formatter: (val) => formatCurrency(val),
          style: {
            fontSize: '12px',
          },
        },
        title: {
          text: 'Cost',
          style: {
            fontWeight: 600,
          },
        },
      },
      {
        // Right Y-axis for usage
        opposite: true,
        labels: {
          formatter: (val) => val.toString(),
          style: {
            fontSize: '12px',
          },
        },
        title: {
          text: 'Usage',
          style: {
            fontWeight: 600,
          },
        },
      },
    ],
    tooltip: {
      y: {
        formatter: (val, opts) => {
          // If it's cost, show currency
          if (opts.seriesIndex === 0) {
            return formatCurrency(val)
          }
          // Otherwise usage
          return `${val}`
        },
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
    },
  }
}
</script>
