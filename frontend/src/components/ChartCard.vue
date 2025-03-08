<script setup>
defineProps({
  title: String,
  chartType: String,
  chartData: Object,
})
</script>

<template>
    <Card>
      <template #content>
        <h3>{{ title }}</h3>
        <Chart :type="chartType" :data="chartData" />
      </template>
    </Card>
</template>
