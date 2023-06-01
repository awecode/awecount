<template>
    <div>
        <canvas id="chartDiagram" ref="chartRef" style="max-height: 300px; width: 100%"></canvas>
    </div>
    <!-- {{ dataComputed }} -->
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
const data = {
    labels: dataComputed.value.labels,
    datasets: [{
        // label: 'My First Dataset',
        data: dataComputed.value.data,
        backgroundColor: dataComputed.value.colors,
        hoverOffset: 4
    }]
};

onMounted(() => {
    //     {
    //   type: 'pie',
    //   data: data,
    // }
    new Chart(chartRef.value, {
        type: 'pie',
        data: data,
    })
})
</script>