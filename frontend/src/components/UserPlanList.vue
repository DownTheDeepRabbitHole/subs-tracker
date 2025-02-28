<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import Select from 'primevue/select'
import InputIcon from 'primevue/inputicon'
import IconField from 'primevue/iconfield'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Slider from 'primevue/slider'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { FilterMatchMode } from '@primevue/core/api'

const categories = ref([])
const userPlans = ref([])
const periodOptions = ref(['Day', 'Month', 'Quarter', 'Year'])

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  plan_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  category_id: { value: null, matchMode: FilterMatchMode.EQUALS },
  period: { value: null, matchMode: FilterMatchMode.EQUALS },
  cost: { value: [0, 100], matchMode: FilterMatchMode.BETWEEN },
  track_usage: { value: null, matchMode: FilterMatchMode.EQUALS },
})

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')
    categories.value = response.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const fetchUserPlans = async () => {
  try {
    // const { category_id, costRange, period } = filters.value
    // console.log(periodOptions.value)
    // console.log(period, typeof period)
    // const queryParams = new URLSearchParams({
    //   cost_min: costRange[0],
    //   cost_max: costRange[1],
    //   ...(category_id && { category_id }),
    //   ...(period && { period: period.toLowerCase() }),
    // }).toString()

    const response = await axios.get(`/api/user-plans/?`)
    userPlans.value = response.data
  } catch (error) {
    console.error('Error fetching user plans:', error)
  }
}

const deleteUserPlan = async (planId) => {
  try {
    await axios.delete(`/api/user-plans/${planId}/`)
    fetchUserPlans()
  } catch (error) {
    console.error('Error deleting user plan:', error)
  }
}

const getCategoryName = (categoryId) => {
  const category = categories.value.find((cat) => cat.id === categoryId)
  return category ? category.name : 'Unknown'
}

onMounted(() => {
  fetchUserPlans()
  fetchCategories()
})
</script>

<template>
    <DataTable
      v-model:filters="filters"
      :value="userPlans"
      paginator
      :rows="10"
      dataKey="id"
      filterDisplay="row"
      removableSort
    >
      <template #header>
        <div class="flex justify-between items-center">
          <div class="w-1/3">
            <IconField>
              <InputIcon>
                <i class="pi pi-search" />
              </InputIcon>
              <InputText v-model="filters['global'].value" placeholder="Search..." />
            </IconField>
          </div>
        </div>
      </template>

      <Column field="plan_name" header="Plan Name" sortable filterField="plan_name">
        <template #body="{ data }">
          <div class="flex items-center space-x-2">
            <img :src="data.icon_url" alt="data.plan_name" class="w-10 rounded-full" />
            <div>
              <b>{{ data.plan_name }}</b>
              <p class="text-sm text-medium-grey">{{ data.subscription_name }}</p>
            </div>
          </div>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            @input="filterCallback()"
            placeholder="Search by name"
          />
        </template>
      </Column>

      <Column
        field="category_id"
        header="Category"
        filterField="category_id"
        :showFilterMenu="false"
      >
        <template #body="{ data }">
          {{ getCategoryName(data.category_id) }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Select
            v-model="filterModel.value"
            @change="filterCallback()"
            :options="categories"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Category"
            showClear
          />
        </template>
      </Column>

      <Column field="payment_date" header="Next Payment Date" sortable></Column>

      <Column field="cost" header="Cost" sortable filterField="cost" :showFilterMenu="false">
        <template #filter="{ filterModel, filterCallback }">
          <div class="min-w-40 grid grid-flow-dense">
            <div class="mb-5">
              <Slider v-model="filterModel.value" @change="filterCallback()" range class="w-full" />
            </div>
            <div class="flex items-center justify-between px-2">
              <InputNumber
                v-model="filterModel.value[0]"
                :min="0"
                :max="filterModel.value[1]"
                @input="filterCallback()"
                fluid
                class="w-[4rem]"
              />
              -
              <InputNumber
                v-model="filterModel.value[1]"
                :min="filterModel.value[0]"
                :max="100"
                @input="filterCallback()"
                fluid
                class="w-[4rem]"
              />
            </div>
          </div>
        </template>
      </Column>

      <Column field="period" header="Period" filterField="period" :showFilterMenu="false">
        <template #filter="{ filterModel, filterCallback }">
          <Select
            v-model="filterModel.value"
            @change="filterCallback()"
            :options="periodOptions"
            placeholder="Select Period"
            showClear
          />
        </template>
      </Column>

      <Column field="usage_score" header="Usage Score" sortable></Column>

      <Column field="track_usage" header="Track Usage">
        <template #body="{ data }">
          <i
            class="pi"
            :class="{
              'pi-check-circle text-green-500': data.track_usage,
              'pi-times-circle text-red-400': !data.track_usage,
            }"
          ></i>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Checkbox v-model="filterModel.value" binary @change="filterCallback()" />
        </template>
      </Column>

      <Column header="Actions">
        <template #body="{ data }">
          <Button
            @click="deleteUserPlan(data.id)"
            icon="pi pi-times"
            severity="danger"
            rounded
            variant="outlined"
            aria-label="Cancel"
          />
        </template>
      </Column>
    </DataTable>
</template>
