<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="p-6 bg-green-50 border border-green-200 rounded-lg">
    <div class="flex items-center">
      <i class="pi pi-check-circle text-green-500 text-2xl mr-3"></i>
      <div>
        <h3 class="text-xl font-semibold text-green-700">{{ title }}</h3>
        <p class="text-green-600">
          <slot></slot>
        </p>
      </div>
    </div>
  </div>
</template>
