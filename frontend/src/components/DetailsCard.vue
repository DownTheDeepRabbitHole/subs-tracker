<!-- BaseDetailsCard.vue -->
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useSubscriptionManager } from '@/composables'

import FieldWrapper from '@/components/FieldWrapper.vue'

const {
  subscriptions,
  categories,
  fetchCategories,
  fetchSubscriptions,
  createSubscription,
  updateSubscriptionCategory,
} = useSubscriptionManager()

const props = defineProps({
  data: {
    type: Object,
    default: {},
  },
  onSubmit: {
    type: Function,
    default: () => {},
  },
  disabledFields: {
    type: Array,
    default: () => [],
  },
  label: {
    type: String,
    default: '',
  },
})

const periodOptions = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Year', value: 'year' },
]
const filteredSubs = ref([])
const showDialog = ref(false)

const form = reactive({
  plan: {
    id: null,
    name: '',
    cost: 0,
    period: '',
    subscription: null,
    freeTrial: false,
  },
  userPlan: {
    paymentDate: null,
    trackUsage: false,
  },
  subscription: {
    name: '',
    category: null,
  },
})

onMounted(async () => {
  await fetchCategories()
  await fetchSubscriptions()

  Object.assign(form, props.data) // Update form with passed in values. Source: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign
  form.plan.subscription = subscriptions.value.find((s) => s.id === form.plan.subscription)
})

// Watch the subscription selection and update the category accordingly
watch(
  () => form.plan.subscription?.category || form.plan.subscription,
  (newSub) => {
    if (newSub) {
      form.subscription.category = newSub.category || null
    } else {
      form.subscription.category = null
    }
  },
)

// When category is set, sends patch update to the backend
const currentCategory = computed({
  get: () => form.plan.subscription?.category || form.subscription.category,
  set: async (newCategory) => {
    if (form.plan.subscription && newCategory !== form.plan.subscription.category) {
      try {
        const updated = await updateSubscriptionCategory(form.plan.subscription.id, newCategory)
        form.plan.subscription.category = updated.category
      } catch (error) {
        console.error('Error updating subscription category:', error)
      }
    } else {
      form.subscription.category = newCategory
    }
  },
})

// AutoComplete search for subscriptions
const searchSubscriptions = (event) => {
  const query = event.query.toLowerCase()
  filteredSubs.value = subscriptions.value.filter((sub) => sub.name.toLowerCase().includes(query))
}

// Create a new subscription
const handleCreateSubscription = async () => {
  try {
    const newSub = await createSubscription(form.subscription.name, form.subscription.category)
    form.plan.subscription = newSub
    form.subscription = { name: '', category: null }
    showDialog.value = false
  } catch (error) {
    console.error('Error creating subscription:', error)
  }
}
</script>

<template>
  <Card class="p-4">
    <template #header>
      <h2>{{ props.label }}</h2>
    </template>
    <template #content>
      <!-- Subscription Field -->
      <FieldWrapper title="Subscription">
        <AutoComplete
          v-model="form.plan.subscription"
          :suggestions="filteredSubs"
          optionLabel="name"
          @complete="searchSubscriptions"
          :disabled="disabledFields.includes('subscription')"
          forceSelection
          placeholder="Enter or select a subscription"
          inputClass="!border-none text-right w-full"
          class="w-full"
        >
          <template #option="slotProps">
            <div class="flex flex-1 items-center justify-between">
              <img
                :alt="slotProps.option.name"
                :src="slotProps.option.icon_url"
                class="w-6 h-6 mr-2 rounded"
              />
              <div>{{ slotProps.option.name }}</div>
            </div>
          </template>
        </AutoComplete>
        <Button icon="pi pi-plus" variant="text" @click="showDialog = true" />
      </FieldWrapper>

      <!-- Category Picker (disabled if no subscription is selected) -->
      <FieldWrapper title="Category">
        <Select
          v-model="currentCategory"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          placeholder="Select category"
          class="border-none"
          inputClass="!border-none text-right"
          :disabled="!form.plan.subscription || disabledFields.includes('subscription')"
        />
      </FieldWrapper>

      <!-- Plan Name -->
      <FieldWrapper title="Plan Name">
        <InputText
          v-model="form.plan.name"
          :disabled="disabledFields.includes('plan')"
          placeholder="Enter plan name"
          class="flex-grow text-right border-none w-full"
        />
      </FieldWrapper>

      <!-- Cost -->
      <FieldWrapper title="Cost">
        <InputNumber
          v-model="form.plan.cost"
          mode="currency"
          currency="CAD"
          placeholder="Enter cost"
          :disabled="disabledFields.includes('plan')"
          inputClass="!border-none text-right w-full"
          class="w-full"
        />
      </FieldWrapper>

      <!-- Period -->
      <FieldWrapper title="Period">
        <Select
          v-model="form.plan.period"
          :options="periodOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select period"
          inputClass="!border-none text-right"
          class="border-none"
          :disabled="disabledFields.includes('plan')"
        />
      </FieldWrapper>

      <!-- Next Payment Date -->
      <FieldWrapper title="Next Payment Date">
        <DatePicker
          v-model="form.userPlan.paymentDate"
          dateFormat="yy-mm-dd"
          placeholder="yy-mm-dd"
          inputClass="!border-none text-right w-full"
          class="w-full"
          showIcon
          iconDisplay="input"
          :disabled="disabledFields.includes('userPlan')"
        />
      </FieldWrapper>

      <!-- Track Usage Toggle -->
      <FieldWrapper title="Track Usage">
        <ToggleSwitch
          v-model="form.userPlan.trackUsage"
          :disabled="disabledFields.includes('userPlan')"
        />
      </FieldWrapper>

      <!-- Free Trial Toggle -->
      <FieldWrapper title="Free Trial">
        <ToggleSwitch v-model="form.plan.freeTrial" :disabled="disabledFields.includes('plan')" />
      </FieldWrapper>

      <!-- Action Button -->
      <div class="mt-6">
        <Button :label="props.label" class="w-full p-button-primary" @click="onSubmit(form)" />
      </div>
    </template>
  </Card>

  <!-- New Subscription Dialog -->
  <Dialog v-model:visible="showDialog" header="Add New Subscription" modal closable class="w-1/2">
    <div class="p-4 space-y-5">
      <div class="flex items-center">
        <label class="w-1/3 font-semibold">Subscription Name</label>
        <InputText
          v-model="form.subscription.name"
          placeholder="Enter subscription name"
          class="flex-1 border-b focus:outline-none"
        />
      </div>
      <div class="flex items-center">
        <label class="w-1/3 font-semibold">Category</label>
        <Select
          v-model="form.subscription.category"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          placeholder="Select a category"
          class="flex-1"
        />
      </div>
    </div>
    <template #footer>
      <div class="flex justify-end space-x-3">
        <Button label="Cancel" icon="pi pi-times" text @click="showDialog = false" />
        <Button
          label="Submit"
          icon="pi pi-check"
          class="p-button-primary"
          @click="handleCreateSubscription"
        />
      </div>
    </template>
  </Dialog>
</template>
