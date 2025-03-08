<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div v-if="title">
    <h2 class="text-md font-semibold uppercase tracking-wide text-gray-600">{{ props.title }}</h2>
    <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ props.subtitle }}</p>
  </div>

  <Card class="p-4 overflow-x-auto">
    <template #content><slot></slot></template>
  </Card>
</template>
