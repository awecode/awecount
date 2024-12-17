<template>
  <div>
    <q-input :model-value="getDateValue" @onClick="this.select()" :error="props.error"
      :error-message="props.errorMessage" :hint="props.hint" :placeholder="props.placeholder" :disable="props.disable"
      @update:model-value="onDateInput" :label="props.label" type="text" class="full-width" mask="####-##-##"
      debounce="1000">
      <template v-slot:append v-if="notRequired && !!getDateValue">
        <q-icon class="cursor-pointer" name="close" @click="onDateInput('')" />
      </template>
    </q-input>
    <q-menu v-if="!props.disable" :no-focus="true" ref="menuRef">
      <q-date v-if="isCalendarInAD" v-model="date" mask="YYYY-MM-DD" :options="toDateValidation" />
      <bs-date-picker v-else v-model="date" :toLimit="props.toLimit" @closeMenu="menuRef.hide()"></bs-date-picker>
    </q-menu>
  </div>
</template>

<script setup>
import BsDatePicker from 'src/components/date/BsDatePicker.vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

const menuRef = ref(null)
const store = useLoginStore()
const props = defineProps([
  'toLimit',
  'modelValue',
  'label',
  'error',
  'errorMessage',
  'hint',
  'placeholder',
  'disable',
  'dateType',
  'notRequired'
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
  if (val === null && props.notRequired) {
  }
  else if (isCalendarInAD.value) {
    if (DateConverter.isValidAD(val)) {
      error.value = false
      errorMessage.value = null
      menuRef.value.hide()
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
  if (text === '' && props.notRequired) {
    date.value = null
    return
  }
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

const toDateValidation = (date) => {
  if (props.toLimit) {
    return (date >= props.toLimit.replaceAll('-', '/')) || ('1944/04/13' < date && date < '2033/04/14')
  }
  else return '1944/04/13' < date && date < '2033/04/14'
}
</script>
