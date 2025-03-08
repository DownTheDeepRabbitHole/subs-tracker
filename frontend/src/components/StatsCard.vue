<script setup>
defineProps({
  title: String,
  amount: Number,
})
</script>

<template>
  <div class="p-col-12 p-md-4">
    <Card>
      <template #content>
        <h3>{{ title }}</h3>
        <h1 class="big-number">${{ amount }}</h1>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.big-number {
  font-size: 3rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 1rem 0;
}
</style>
