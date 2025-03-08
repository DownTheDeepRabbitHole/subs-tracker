<script setup>
import { ref, computed } from 'vue'

import { useFormatting } from '@/composables/useFormatting'

const { formatCurrency } = useFormatting()

const props = defineProps({
  categories: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

// Transform the category object into an array for DataTable
const tableData = computed(() => {
  console.log(props.categories)
  if (!props.categories || Object.keys(props.categories).length === 0) {
    return []
  }

  return Object.entries(props.categories).map(([name, data]) => ({
    name,
    percentage: data.percentage,
    cost: data.cost,
    icon: data.icon || '📊',
  }))
})

// Check if we have data
const hasData = computed(() => tableData.value.length > 0)

// Sort options
const sortOptions = ref([
  { label: 'Highest Cost', value: 'cost:desc' },
  { label: 'Lowest Cost', value: 'cost:asc' },
  { label: 'Category A-Z', value: 'name:asc' },
  { label: 'Percentage', value: 'percentage:desc' },
])
const sortKey = ref('cost:desc')

// Custom color mapping for percentage tags
const getColorForPercentage = (percentage) => {
  if (percentage >= 50) return 'danger'
  if (percentage >= 25) return 'warning'
  if (percentage >= 10) return 'info'
  return 'success'
}
</script>

<template>
  <div class="category-table">
    <div class="flex justify-between items-center mb-4">
      <div v-if="hasData">
        <Select
          v-model="sortKey"
          :options="sortOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Sort by"
          class="p-inputtext-sm"
        />
      </div>
    </div>

    <div v-if="!hasData && !loading" class="py-6 text-center bg-gray-50 rounded-lg">
      <p class="text-gray-500">No category data available.</p>
    </div>

    <DataTable
      v-else
      :value="tableData"
      :loading="loading"
      :sortField="sortKey.split(':')[0]"
      :sortOrder="sortKey.split(':')[1] === 'desc' ? -1 : 1"
      class="p-datatable-sm"
      responsiveLayout="scroll"
      removableSort
    >
      <Column field="name" header="Category" sortable>
        <template #body="{ data }">
          <div class="flex items-center">
            <span class="text-xl mr-2">{{ data.icon }}</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </Column>

      <Column field="percentage" header="% of Spend" sortable>
        <template #body="{ data }">
          <Tag
            :value="`${data.percentage.toFixed(1)}%`"
            :severity="getColorForPercentage(data.percentage)"
            class="text-xs"
          />
        </template>
      </Column>

      <Column field="cost" header="Cost" sortable class="text-right">
        <template #body="{ data }">
          <span class="font-semibold">{{ formatCurrency(data.cost) }}</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
/* Add some custom styling to match Stripe/Rocket Money UI */
:deep(.p-datatable) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.05em;
  font-weight: 600;
  color: #64748b;
  padding: 0.75rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  transition: background-color 0.15s;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f1f5f9;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.p-tag) {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

:deep(.p-dropdown) {
  font-size: 0.875rem;
}
</style>
