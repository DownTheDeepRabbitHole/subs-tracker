<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FilterMatchMode } from '@primevue/core/api'
import { formatDistanceToNow } from 'date-fns'

import { useSubscriptionManager } from '@/composables'

const { deleteUserPlan, toggleUsage } = useSubscriptionManager()

const router = useRouter()

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
    required: false,
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
  showHeaders: {
    type: Boolean,
    required: false,
    default: true,
  },
  paginator: {
    type: Boolean,
    required: false,
    default: true,
  },
})

// Chooses which columns to display from the fields prop
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
    period: { value: '', matchMode: FilterMatchMode.EQUALS },
    track_usage: { value: null, matchMode: FilterMatchMode.EQUALS },
    payment_date: { value: null, matchMode: FilterMatchMode.BETWEEN },
  }
}
initFilters()

// Computes the maximum cost from user plans for cost range slider
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

// Compute a color for usage score (0: red, 10: green)
const getUsageColor = (score) => {
  const green = Math.floor((score / 10) * 255)
  const red = 255 - green
  return `rgb(${red}, ${green}, 0)`
}

const clearFilter = () => {
  initFilters()
}

const handlePeriodChange = () => {
  console.log('New period:', filters.value.period.value)
  emit('refresh', { period: filters.value.period.value })
}

const handleDelete = async (planId) => {
  await deleteUserPlan(planId)
  emit('refresh')
}

const handleEdit = (planId) => {
  router.push({ name: 'edit plan', params: { planId } })
}

const handleToggleUsage = async (plan) => {
  await toggleUsage(plan.id, plan.track_usage)
  emit('refresh')
}
</script>

<template>
  <DataTable
    v-model:filters="filters"
    :value="userPlans"
    :rows="10"
    :rowsPerPageOptions="[10, 20, 50]"
    dataKey="id"
    filterDisplay="menu"
    :globalFilterFields="['subscription_name', 'plan_name']"
    removableSort
    class="sm:p-datatable-sm mx-auto w-full"
    :showHeaders="showHeaders"
    :paginator="paginator"
  >
    <!-- Header with Global Search and "Clear Filters" button -->
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
      :filterField="
        col.field === 'category'
          ? 'category_id'
          : col.field === 'usage_score'
            ? 'track_usage'
            : col.field
      "
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

      <!-- Payment Date Column -->
      <template v-else-if="col.field === 'payment_date'" #body="{ data }">
        <div class="text-sm">{{ formatPaymentDate(data.payment_date) }}</div>
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
        <div class="flex items-center space-x-2">
          <Button
            @click="handleEdit(data.id)"
            icon="pi pi-pencil"
            severity="secondary"
            class="w-8 h-8"
            aria-label="Edit plan"
          />
          <Button
            @click="handleDelete(data.id)"
            icon="pi pi-trash"
            severity="danger"
            class="w-8 h-8"
            aria-label="Delete plan"
          />
        </div>
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
              v-model="filters.period.value"
              @change="handlePeriodChange"
              :options="periodOptions"
              optionLabel="label"
              optionValue="value"
            />
          </div>
        </div>
      </template>

      <!-- Filter Category -->
      <template v-if="showFilters && col.field === 'category'" #filter="{ filterModel }">
        <div class="p-2">
          <label class="text-xs block mb-1">Category:</label>
          <Select
            v-model="filterModel.value"
            :options="categories"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Category"
            class="w-full"
            showClear
          />
        </div>
      </template>

      <!-- Filter Payment Date -->
      <template v-if="showFilters && col.field === 'payment_date'" #filter="{ filterModel }">
        <div class="p-2">
          <label class="text-xs block mb-1">Due Date Range:</label>
          <DatePicker
            v-model="filterModel.value"
            selectionMode="range"
            dateFormat="yy-mm-dd"
            inline
            class="w-full"
          />
        </div>
      </template>

      <!-- Filter Usage Column -->
      <template v-if="showFilters && col.field === 'usage_score'" #filter="{ filterModel }">
        <div class="p-2">
          <label class="text-xs block mb-1">Usage:</label>
          <Select
            v-model="filterModel.value"
            :options="[
              { label: 'Any', value: null },
              { label: 'On', value: true },
              { label: 'Off', value: false },
            ]"
            optionLabel="label"
            optionValue="value"
            placeholder="Select Usage"
            class="w-full"
          />
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
