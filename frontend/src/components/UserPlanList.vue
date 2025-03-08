<script setup>
import { ref, computed, watch } from 'vue'

import { FilterMatchMode } from '@primevue/core/api'
import { formatDistanceToNow } from 'date-fns'

import { useSubscriptionManager } from '@/composables/useSubscriptionManager'

const { deleteUserPlan, toggleUsage } = useSubscriptionManager()

const periodOptions = [
  { label: 'Any', value: '' },
  { label: 'Day', value: 'day' },
  { label: 'Month', value: 'month' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Year', value: 'year' },
]

const columns = {
  plan: { field: 'plan', header: 'Plan', sortable: false },
  category: { field: 'category', header: 'Category', sortable: false },
  payment_date: { field: 'payment_date', header: 'Due', sortable: true },
  cost: { field: 'cost', header: 'Cost/Period', sortable: true },
  usage_score: { field: 'usage_score', header: 'Usage', sortable: true },
  actions: { field: 'actions', header: 'Actions', sortable: false },
}

const props = defineProps({
  userPlans: {
    type: Array,
    required: true,
    default: () => [],
  },
  categories: {
    type: Array,
    required: true,
    default: () => [],
  },
  fields: {
    type: Array,
    required: false,
    default: () => ['plan', 'category', 'payment_date', 'cost', 'usage_score', 'actions'],
  },
  showFilters: {
    type: Boolean,
    required: false,
    default: true,
  },
})

const visibleColumns = computed(() => {
  return props.fields.map((field) => columns[field]).filter((col) => col !== undefined)
})

const emit = defineEmits(['refresh'])

const filters = ref({})
const initFilters = () => {
  filters.value = {
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    category_id: { value: null, matchMode: FilterMatchMode.EQUALS },
    cost: { value: [0, 100], matchMode: FilterMatchMode.BETWEEN },
    period: '',
  }
}
initFilters()

// Compute the maximum cost from user plans
const costMax = computed(() => {
  if (props.userPlans.length) {
    return Math.max(...props.userPlans.map((plan) => plan.cost))
  }
  return 100
})

watch(
  () => props.userPlans,
  () => {
    filters.value.cost.value = [0, costMax.value]
  },
  { immediate: true },
)

const getCategoryName = (categoryId) => {
  const cat = props.categories.find((c) => c.id === categoryId)
  return cat ? cat.name : 'Unknown'
}

const formatPaymentDate = (date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

// Compute a color for usage score (0:red, 10:green).
const getUsageColor = (score) => {
  const green = Math.floor((score / 10) * 255)
  const red = 255 - green
  return `rgb(${red}, ${green}, 0)`
}

const clearFilter = () => {
  initFilters()
}

const handlePeriodChange = () => {
  console.log('New period:', filters.value.period)
  emit('refresh', { period: filters.value.period })
}

const handleDelete = async (planId) => {
  await deleteUserPlan(planId)
  emit('refresh')
}

const handleToggleUsage = async (plan) => {
  await toggleUsage(plan.id, plan.track_usage)
  emit('refresh')
}
</script>

<style scoped>
/* Adjust text sizing for compact cells */
.text-xs {
  line-height: 1.2;
}

/* Example responsive adjustments */
@media (min-width: 640px) {
  .column-cell {
    padding: 0.5rem !important;
  }
}
</style>

<template>
  <DataTable
    v-model:filters="filters"
    :value="userPlans"
    paginator
    :rows="10"
    :rowsPerPageOptions="[10, 20, 50]"
    dataKey="id"
    filterDisplay="menu"
    :globalFilterFields="['subscription_name', 'plan_name']"
    removableSort
    class="sm:p-datatable-sm mx-auto w-full"
  >
    <!-- Header with Global Search and Clear Filters Button -->
    <template #header v-if="showFilters">
      <div class="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
        <div class="w-full sm:w-1/3">
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText
              v-model="filters.global.value"
              placeholder="Search plans..."
              class="w-full"
            />
          </IconField>
        </div>
        <Button
          type="button"
          icon="pi pi-filter-slash"
          label="Clear"
          outlined
          @click="clearFilter"
        />
      </div>
    </template>

    <!-- Dynamic Columns -->
    <Column
      v-for="col in visibleColumns"
      :key="col.field"
      :field="col.field"
      :header="col.header"
      :sortable="showFilters && col.sortable"
      :showFilterMatchModes="false"
      class="column-cell"
    >
      <!-- Plan Column -->
      <template v-if="col.field === 'plan'" #body="{ data }">
        <div class="flex items-center space-x-3">
          <img
            :src="data.icon_url"
            :alt="data.plan_name"
            class="w-10 h-10 rounded-lg object-cover"
          />
          <div>
            <div class="font-semibold text-sm">{{ data.plan_name }}</div>
            <div class="text-xs text-gray-500">{{ data.subscription_name }}</div>
          </div>
        </div>
      </template>

      <!-- Category Column -->
      <template v-else-if="col.field === 'category'" #body="{ data }">
        <Tag class="text-sm">
          {{ getCategoryName(data.category_id) }}
        </Tag>
      </template>

      <!-- Due Column -->
      <template v-else-if="col.field === 'payment_date'" #body="{ data }">
        <div>
          <div class="text-sm">{{ formatPaymentDate(data.payment_date) }}</div>
        </div>
      </template>

      <!-- Cost/Period Column -->
      <template v-else-if="col.field === 'cost'" #body="{ data }">
        <div class="text-sm">
          {{ '$' + data.cost }}
          <span class="text-xs text-gray-500">
            / {{ data.period ? data.period.toLowerCase() : 'month' }}
          </span>
        </div>
      </template>

      <!-- Usage Column -->
      <template v-else-if="col.field === 'usage_score'" #body="{ data }">
        <div @click="handleToggleUsage(data)" class="flex items-center space-x-2 cursor-pointer">
          <div v-if="data.track_usage">
            <span
              class="text-xs font-bold text-white rounded-full px-2 py-1"
              :style="{ backgroundColor: getUsageColor(data.usage_score) }"
            >
              {{ data.usage_score }}/10
            </span>
          </div>
          <div v-else>
            <span class="text-xs text-gray-500">Off</span>
          </div>
        </div>
      </template>

      <!-- Actions Column -->
      <template v-else-if="col.field === 'actions'" #body="{ data }">
        <Button
          @click="handleDelete(data.id)"
          icon="pi pi-trash"
          severity="danger"
          rounded
          outlined
          aria-label="Delete plan"
        />
      </template>

      <!-- Filter Template for Cost/Period Column -->
      <template v-if="showFilters && col.field === 'cost'" #filter="{ filterModel }">
        <div class="flex flex-col space-y-2 p-2">
          <!-- Cost Range Filter -->
          <div>
            <label class="text-xs block mb-1">Cost Range:</label>
            <Slider v-model="filterModel.value" range class="w-full" />
            <div class="flex justify-between mt-1">
              <InputNumber v-model="filterModel.value[0]" inputClass="w-16" :min="0" />
              <InputNumber
                v-model="filterModel.value[1]"
                inputClass="w-16"
                :min="filterModel.value[0]"
                :max="costMax"
              />
            </div>
          </div>
          <!-- Period Filter -->
          <div>
            <label class="text-xs block mb-1">Period:</label>
            <Select
              v-model="filters.period"
              @change="handlePeriodChange"
              :options="periodOptions"
              optionLabel="label"
              optionValue="value"
            />
          </div>
        </div>
      </template>
    </Column>

    <!-- Empty State -->
    <template #empty>
      <div class="flex flex-col items-center justify-center py-6">
        <i class="pi pi-inbox text-4xl text-gray-400" />
        <p class="mt-2 text-gray-500">No plans found</p>
      </div>
    </template>
  </DataTable>
</template>
