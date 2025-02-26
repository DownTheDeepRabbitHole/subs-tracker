<template>
  <div>DSFSD</div>
  <div :class="boxClasses">This is a dynamically styled box.</div>

  <button @click="toggleClass">Toggle Box Style</button>
</template>

<script setup>
import { ref, computed } from 'vue'

const isActive = ref(false)

const boxClasses = computed(() => {
  return {
    'bg-blue-500': isActive.value,
    'bg-gray-300': !isActive.value,
    'text-white': true, // Keep text white regardless of isActive
    'p-4': true, // Always have padding
    'rounded-lg': true, // Always have rounded corners
  }
})

const toggleClass = () => {
  isActive.value = !isActive.value
}
</script>
