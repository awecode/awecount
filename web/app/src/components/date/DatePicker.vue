<template>
  <div>
    <q-input
      :model-value="getDateValue"
      @onClick="this.select()"
      :error="props.error"
      :error-message="props.errorMessage"
      :hint="props.hint"
      :placeholder="props.placeholder"
      :disable="props.disable"
      @update:model-value="onDateInput"
      :label="props.label"
      type="text"
      class="full-width"
    >
    </q-input>
    <q-menu v-if="!props.disable" :no-focus="true">
      <q-date v-if="isCalendarInAD" v-model="date" mask="YYYY-MM-DD" />
      <bs-date-picker v-else v-model="date"></bs-date-picker>
    </q-menu>
  </div>
</template>
<script setup>
import BsDatePicker from '/src/components/date/BsDatePicker.vue'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

const store = useLoginStore()
const props = defineProps([
  'modelValue',
  'label',
  'error',
  'errorMessage',
  'hint',
  'placeholder',
  'disable',
  'dateType',
])
const date = ref(props.modelValue)
const error = ref(props.error)
const errorMessage = ref(props.errorMessage)

const emit = defineEmits(['update:modelValue'])
const isCalendarInAD = computed(() => {
  if (!store?.isCalendarInAD || props.dateType === 'bs') {
    return false
  } else {
    return true
  }
})

watch(date, (val) => {
  if (isCalendarInAD.value) {
    if (DateConverter.isValidAD(val)) {
      error.value = false
      errorMessage.value = null
    }
  } else {
    if (DateConverter.isValid(val)) {
      error.value = false
      errorMessage.value = null
    }
  }
  emit('update:modelValue', val)
})

watch(
  () => props.modelValue,
  (val) => {
    date.value = val
  }
)

const getDateValue = computed(() => {
  const convertedDate = DateConverter.getRepresentation(
    date.value,
    isCalendarInAD.value ? 'ad' : 'bs'
  )
  return convertedDate
})

const onDateInput = (text) => {
  text = DateConverter.parseText(text)
  error.value = false
  errorMessage.value = null
  if (isCalendarInAD.value) {
    if (DateConverter.isValidAD(text)) {
      date.value = text
      error.value = false
      errorMessage.value = null
    } else {
      error.value = true
      errorMessage.value = 'Invalid AD Date'
    }
  } else {
    if (DateConverter.isValid(text)) {
      date.value = DateConverter.bs2ad(text)
      error.value = false
      errorMessage.value = null
    } else {
      error.value = true
      errorMessage.value = 'Invalid BS Date'
    }
  }
}
</script>
