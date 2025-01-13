<script setup>
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from '/src/stores/login-info.js'

const props = defineProps({
  date: {
    type: String || undefined,
  },
  label: {
    type: String,
    required: true,
  },
})
const store = useLoginStore()
const dateComputed = computed(() => {
  if (store.isCalendarInAD) return props.date
  else return DateConverter.getRepresentation(props.date, 'bs')
})
</script>

<template>
  <q-input
    v-model="dateComputed"
    disable
    type="text"
    :label="props.label"
  />
</template>
