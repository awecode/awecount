<template>
  <div>
    <PrintHeader></PrintHeader>
  </div>
</template>

<script>
import PrintHeader from '/src/components/print/PrintHeader.vue'
export default {
  props: {
    data: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  setup(props) {
    return { props, PrintHeader }
  },
}
</script>
