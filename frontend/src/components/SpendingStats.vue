<script setup>
import { ref, onMounted, computed } from 'vue'
import CardWrapper from './CardWrapper.vue'
import { useSubscriptionManager, useHelpers } from '@/composables'

const { userPlans, fetchUserPlans } = useSubscriptionManager()
const { formatCurrency } = useHelpers()

const selectedPeriod = ref('month')
const periodOptions = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Year', value: 'year' },
]

const apexOptions = ref({})
const apexSeries = ref([])

const totalCostDisplay = computed(() => {
  const total = userPlans.value.reduce((sum, plan) => sum + (plan.cost ?? 0), 0)
  return formatCurrency(total)
})

onMounted(async () => {
  await fetchHighestUserPlans()
  buildChart()
})

const handlePeriodChange = async () => {
  await fetchHighestUserPlans()
  buildChart()
}

const fetchHighestUserPlans = async () => {
  await fetchUserPlans({ period: selectedPeriod.value, page_size: 5 })
}

function buildChart() {
  const maxCost = Math.ceil(Math.max(...userPlans.value.map((plan) => plan.cost ?? 0)))
  const maxUsageScore = Math.ceil(
    Math.max(...userPlans.value.map((plan) => plan.usage_score ?? 0)) * 1.3,
  )

  const categories = userPlans.value.map((plan) => plan.subscription_name)
  const costData = userPlans.value.map((plan) => Number(plan.cost ?? 0))
  const usageData = userPlans.value.map((plan) => Number(plan.usage_score ?? 0))

  apexSeries.value = [
    { name: 'Cost', type: 'column', data: costData },
    { name: 'Usage', type: 'column', data: usageData },
  ]

  apexOptions.value = {
    chart: {
      type: 'bar',
      stacked: true,
      toolbar: { show: false },
    },
    bar: {
      dataLabels: {
        position: 'top',
      },
    },
    annotations: {
      points: userPlans.value.map((plan) => {
        const normalizedUsageScore = (plan.usage_score / maxUsageScore) * maxCost

        const yPos = Math.max(normalizedUsageScore, plan.cost)
        const xPos = plan.subscription_name

        return {
          x: xPos,
          y: yPos,
          marker: {
            size: 0,
            offsetY: 999,
          },
          label: {
            borderColor: '[transparent]',
            offsetY: 2,
            style: {
              color: '#000000',
              fontSize: '15px',
              fontWeight: 'bold',
            },
            text: formatCurrency(plan.cost),
          },
          image: {
            path: plan.icon_url,
            width: 30,
            height: 30,
            offsetY: -40,
          },
        }
      }),
    },
    xaxis: {
      categories,
      labels: {
        rotate: 0,
        trim: true,
      },
    },
    yaxis: [
      {
        seriesName: 'Cost',
        min: 0,
        max: maxCost,
        labels: {
          formatter: (val) => formatCurrency(val),
        },
      },
      {
        seriesName: 'Usage',
        min: 0,
        max: maxUsageScore,
        opposite: true,
        labels: {
          formatter: (val) => val.toFixed(1),
        },
      },
    ],
    tooltip: {
      y: {
        formatter: (val, opts) => (opts.seriesIndex === 0 ? formatCurrency(val) : val),
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
    },
    grid: {
      strokeDashArray: 5,
      xaxis: {
        lines: {
          show: true,
        },
      },
    },
  }
}
</script>

<template>
  <CardWrapper>
    <div class="flex items-center justify-between">
      <!-- Left column: Header with Select -->
      <div class="flex flex-col items-center space-y-2">
        <div class="text-xl font-semibold text-gray-800">{{ totalCostDisplay }} per</div>
        <Select
          v-model="selectedPeriod"
          :options="periodOptions"
          optionLabel="label"
          optionValue="value"
          @change="handlePeriodChange"
          class="w-32 p-2 rounded-md border-none bg-gray-100 focus:ring-2"
        />
      </div>

      <!-- Right column: Bar Chart -->
      <div class="flex-1">
        <apexchart v-if="apexOptions && apexSeries.length" type="bar" height="200" :options="apexOptions" :series="apexSeries" />
      </div>
    </div>
  </CardWrapper>
</template>
