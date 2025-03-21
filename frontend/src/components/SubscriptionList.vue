<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubscriptionManager, useHelpers } from '@/composables'
import { useRouter } from 'vue-router'

const { subscriptions, categories, addToUserPlans, getCategoryName, deletePlan, initData } =
  useSubscriptionManager()
const { showToast } = useHelpers()

const router = useRouter()

const layout = ref('grid')
const options = ref(['list', 'grid'])

const sortKey = ref({ label: 'Subscription Name (A-Z)', value: 'name' })
const sortOptions = ref([
  { label: 'Subscription Name (A-Z)', value: 'name' },
  { label: 'Plan Count High to Low', value: '!plans' },
  { label: 'Plan Count Low to High', value: 'plans' },
])
const searchQuery = ref('')

const showDateDialog = ref(false)
const selectedPlan = ref(null)
const nextPaymentDate = ref(null)
const today = ref(new Date())

const onSortChange = (event) => {
  sortKey.value = event.value
}

const handleAddToUserPlans = async () => {
  if (!nextPaymentDate.value) {
    showToast('error', 'Error', 'Please select a next payment date')
    return
  }
  const success = await addToUserPlans(selectedPlan.value.id, nextPaymentDate.value)
  if (success) {
    showDateDialog.value = false
    nextPaymentDate.value = null
    selectedPlan.value = null
  }
}

// Navigate to edit view
const handleEditPlan = (plan) => {
  router.push({ name: 'edit plan', params: { planId: plan.id } })
}

// Delete plan with confirmation
const handleDeletePlan = async (plan) => {
  const confirmed = confirm(`Are you sure you want to delete "${plan.name}"?`)
  if (!confirmed) return

  await deletePlan(plan.id)
}

// Computed filtered and sorted subscriptions
const filteredSubscriptions = computed(() => {
  let subs = subscriptions.value || []

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    subs = subs.filter((sub) => {
      const subName = sub.name.toLowerCase()
      const categoryName = getCategoryName(sub.category).toLowerCase()
      const planMatch =
        sub.plans && sub.plans.some((plan) => plan.name.toLowerCase().includes(query))
      return subName.includes(query) || categoryName.includes(query) || planMatch
    })
  }

  if (sortKey.value) {
    const value = sortKey.value.value
    if (value === 'name') {
      subs = subs.slice().sort((a, b) => {
        const aHasPlans = a.plans && a.plans.length > 0
        const bHasPlans = b.plans && b.plans.length > 0
        if (aHasPlans !== bHasPlans) {
          return aHasPlans ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      })
    } else if (value === '!plans') {
      subs = subs
        .slice()
        .sort((a, b) => (b.plans ? b.plans.length : 0) - (a.plans ? a.plans.length : 0))
    } else if (value === 'plans') {
      subs = subs
        .slice()
        .sort((a, b) => (a.plans ? a.plans.length : 0) - (b.plans ? b.plans.length : 0))
    }
  }

  return subs
})

const openDateDialog = (plan) => {
  selectedPlan.value = plan
  showDateDialog.value = true
}

onMounted(() => {
  initData()
})
</script>

<template>
  <DataView :value="filteredSubscriptions" paginator :rows="8" :layout="layout">
    <template #header>
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6">
        <div class="flex items-center gap-4">
          <Button label="Add Plan" icon="pi pi-plus" @click="$router.push('/add-plan')" />
          <Select
            v-model="sortKey"
            :options="sortOptions"
            optionLabel="label"
            placeholder="Sort Subscriptions"
            @change="onSortChange"
          />
        </div>
        <div class="flex items-center gap-4 mt-4 sm:mt-0">
          <InputText
            v-model="searchQuery"
            placeholder="Search by subscription, plan, or category"
          />
          <SelectButton
            v-model="layout"
            :options="options"
            :allowEmpty="false"
            class="p-selectbutton-sm"
          >
            <template #option="{ option }">
              <i :class="['text-sm p-2', option === 'list' ? 'pi pi-bars' : 'pi pi-th-large']" />
            </template>
          </SelectButton>
        </div>
      </div>
    </template>

    <!-- List Layout -->
    <template #list="slotProps">
      <div
        v-for="(item, index) in slotProps.items"
        :key="index"
        class="border-b last:border-b-0 border-gray-300 hover:bg-gray-50 transition-colors"
      >
        <div class="p-4">
          <div class="flex items-center gap-4">
            <img :src="item.icon_url" :alt="item.name" class="w-8 h-8 rounded-lg" />
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">{{ item.name }}</h3>
              <p class="text-sm text-gray-500">{{ getCategoryName(item.category) }}</p>
            </div>
          </div>
          <div class="ml-12 mt-3 space-y-3">
            <div
              v-for="plan in item.plans"
              :key="plan.id"
              class="flex items-center justify-between group"
            >
              <div>
                <span class="font-medium text-gray-900">{{ plan.name }}</span>
                <span class="text-sm text-gray-500 ml-2">
                  (${{ plan.cost }} / {{ plan.period }})
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <Button
                  icon="pi pi-pencil"
                  class="p-button-text text-blue-500 hover:text-blue-700 !w-8 !h-8"
                  @click="handleEditPlan(plan)"
                />
                <Button
                  icon="pi pi-trash"
                  class="p-button-text text-red-500 hover:text-red-700 !w-8 !h-8"
                  @click="handleDeletePlan(plan)"
                />
                <Button
                  icon="pi pi-plus"
                  class="p-button-text text-primary-500 hover:text-primary !w-8 !h-8"
                  @click="openDateDialog(plan)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Grid Layout -->
    <template #grid="slotProps">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div
          v-for="(item, index) in slotProps.items"
          :key="index"
          class="bg-white rounded-lg border border-gray-300 hover:border-gray-400 transition-all hover:shadow-sm"
        >
          <div class="p-4">
            <div class="flex items-center gap-3 mb-4">
              <img :src="item.icon_url" :alt="item.name" class="w-8 h-8 rounded-lg" />
              <div>
                <h3 class="font-semibold text-gray-900">{{ item.name }}</h3>
                <p class="text-sm text-gray-500">{{ getCategoryName(item.category) }}</p>
              </div>
            </div>
            <div class="space-y-3">
              <div
                v-for="plan in item.plans"
                :key="plan.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
              >
                <div>
                  <span class="font-medium text-gray-900 block">{{ plan.name }}</span>
                  <span class="text-sm text-gray-500"> ${{ plan.cost }} / {{ plan.period }} </span>
                </div>
                <div class="flex items-center space-x-2">
                  <Button
                    icon="pi pi-pencil"
                    class="p-button-text text-blue-500 hover:text-blue-700 !w-8 !h-8"
                    @click="handleEditPlan(plan)"
                  />
                  <Button
                    icon="pi pi-trash"
                    class="p-button-text text-red-500 hover:text-red-700 !w-8 !h-8"
                    @click="handleDeletePlan(plan)"
                  />
                  <Button
                    icon="pi pi-plus"
                    class="p-button-text text-gray-400 hover:text-primary !w-8 !h-8"
                    @click="openDateDialog(plan)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </DataView>

  <!-- Add Plan to User List Dialog -->
  <Dialog
    v-model:visible="showDateDialog"
    :modal="true"
    :closable="false"
    class="max-w-md"
    header-class="hidden"
  >
    <div class="px-6 flex flex-col items-center justify-center">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Select next payment date</h3>
      <DatePicker v-model="nextPaymentDate" :minDate="today" dateFormat="yy-mm-dd" inline />
    </div>
    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancel"
          class="p-button-text text-gray-700 hover:text-gray-900"
          @click="showDateDialog = false"
        />
        <Button label="Add to list" icon="pi pi-check" @click="handleAddToUserPlans" />
      </div>
    </template>
  </Dialog>
</template>
