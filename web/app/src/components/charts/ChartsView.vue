<template>
  <div>
    <canvas id="chartDiagram" ref="chartDiagram" style="max-height: 300px; width: 100%"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'
export default {
  props: {
    data: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  setup(props, { emit }) {
    const chartDiagram = ref(null)
    // const labelsComputed = computed(() => {
    //   data.labels.forEach((element) => {
    //     console.log(element)
    //   })
    // })
    const colors = [
      // blue
      'rgba(92, 181, 240, 0.7)',
      // pink
      'rgba(254,128,158, 0.7)',
      //  yellow
      'rgba(254,215,122, 0.7)',
      // green
      'rgba(110,205,205, 0.7)',
      // gray
      'rgba(194,196,209, 0.7)',
      // orange
      'rgba(254,206,162, 0.7)',
      // red
      'rgba(214,55,89, 0.7)',
      // greenish blue
      'rgba(23, 190, 207, 0.7)',
      // purple
      'rgba(148, 103, 189, 0.7)',
      // brown
      'rgba(140, 86, 75, 0.7)',
    ]
    const isSeries = computed(() => {
      return !['pie', 'doughnut', 'polarArea'].includes(props.data.type)
    })
    const multiplyArray = (arr, n) => {
      let newArr = []
        ;[...Array(n)].forEach(() => {
          newArr = newArr.concat(arr)
        })
      return newArr
    }
    const datacomputed = computed(() => {
      let data = props.data
      if (data && data.datasets && data.datasets.length) {
        data.datasets.forEach((dataset, index) => {
          if (isSeries.value) {
            let colorIndex = index % colors.length
            dataset.backgroundColor = colors[colorIndex]
            dataset.borderColor = colors[colorIndex]
            dataset.lineTension = 0
            dataset.fill = false
            if (data.type == 'mixed' && index % 2) {
              dataset.type = 'line'
            }
          } else {
            dataset.backgroundColor = multiplyArray(
              colors,
              Math.ceil(dataset.data.length / colors.length)
            )
          }
        })
      }
      return data
    })
    onMounted(() => {
      // chartDiagram = new
      new Chart(chartDiagram.value, {
        type:
          datacomputed.value.type === 'mixed' ? 'bar' : datacomputed.value.type,
        data: {
          labels: datacomputed.value.labels,
          datasets: datacomputed.value.datasets,
        },
      })
    })
    return { chartDiagram, datacomputed }
  },
}
</script>
