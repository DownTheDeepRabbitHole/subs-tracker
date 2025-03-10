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
  <div class="flex flex-col gap-4">
    <div v-if="title">
      <h3>{{ props.title }}</h3>
      <h4 v-if="subtitle" class="mt-1">{{ props.subtitle }}</h4>
    </div>

    <Card class="overflow-x-auto">
      <template #content><slot></slot></template>
    </Card>
  </div>
</template>
