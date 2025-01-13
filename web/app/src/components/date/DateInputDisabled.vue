<template>
  <q-input type="text" v-model="dateComputed" disable :label="props.label" />
</template>
<script setup>
import { useLoginStore } from 'src/stores/login-info.js'
import DateConverter from 'src/components/date/VikramSamvat.js'
const store = useLoginStore()
const props = defineProps({
  date: {
    type: String || undefined,
  },
  label: {
    type: String,
    required: true,
  },
})
const dateComputed = computed(() => {
  if (store.isCalendarInAD) return props.date
  else return DateConverter.getRepresentation(props.date, 'bs')
})
</script>
