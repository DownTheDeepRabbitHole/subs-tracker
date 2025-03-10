<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="flex justify-between items-center">
    <label class="w-1/3 font-semibold">{{ props.title }}</label>
    <slot></slot>
  </div>
  <Divider />
</template>
