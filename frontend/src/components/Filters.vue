<template>
  <div class="flex justify-between items-center space-x-4 mb-6">
    <!-- Category Filter -->
    <div class="w-1/3">
      <label class="block text-sm font-semibold">Category</label>
      <Select
        id="category"
        v-model="filters.category"
        :options="categories"
        option-label="name"
        option-value="id"
        placeholder="Select Category"
        showClear
        @change="onFilterChange"
        fluid
      />
    </div>

    <!-- Period Filter -->
    <div class="w-1/3">
      <label class="block text-sm font-semibold">Period</label>
      <Select id="period" v-model="filters.period" :options="periodOptions" showClear placeholder="Select Period" @change="onFilterChange" fluid />
    </div>

    <!-- Cost Range Filters -->
    <div class="w-1/3">
      <label class="block text-sm font-semibold">Cost</label>
      <div class="flex items-center space-x-4">
        <InputNumber v-model="filters.costRange[0]" :min="0" :max="filters.costRange[1]" @input="onFilterChange" class="w-1/5" />
        <Slider id="costRange" v-model="filters.costRange" @change="onFilterChange" :min="0" :max="1000" range class="w-3/5" />
        <InputNumber v-model="filters.costRange[1]" :min="filters.costRange[0]" :max="1000" @input="onFilterChange" class="w-1/5" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Select from 'primevue/select'
import Slider from 'primevue/slider'
import InputNumber from 'primevue/inputnumber'

const props = defineProps({
  categories: Array,
  periodOptions: Array,
  filters: Object,
})

const emit = defineEmits(['filter-change'])

const onFilterChange = () => {
  emit('filter-change', props.filters)
}
</script>

<style>
.p-inputnumber input {
  width: 10px;
}
</style>
