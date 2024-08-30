<template>
  <div>
    <canvas id="chartDiagram" ref="chartRef" style="max-height: 300px; width: 100%"></canvas>
  </div>
</template>

<script setup>
import Chart from 'chart.js/auto'
const props = defineProps(['data'])
const chartRef = ref(null)
const dataComputed = computed(() => {
  let data = {
    labels: [],
    data: [],
    colors: []
  }
  props.data.forEach((item) => {
    data.labels.push(item.label)
    data.data.push(item.amount)
    data.colors.push(item.color)
  })
  return data
})
const pieData = {
  labels: dataComputed.value.labels,
  datasets: [{
    // label: 'My First Dataset',
    data: dataComputed.value.data,
    backgroundColor: dataComputed.value.colors,
    hoverOffset: 4
  }]
};

onMounted(() => {
  new Chart(chartRef.value, {
    type: 'pie',
    data: pieData,
  })
})
</script>
