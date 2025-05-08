<script setup>
import BsDatePicker from 'src/components/date/BsDatePicker.vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

const props = defineProps(['toLimit', 'modelValue', 'label', 'error', 'errorMessage', 'hint', 'placeholder', 'disable', 'dateType', 'notRequired'])
const emit = defineEmits(['update:modelValue'])
const menuRef = ref(null)
const store = useLoginStore()
const date = ref(props.modelValue)
const error = ref(props.error)
const errorMessage = ref(props.errorMessage)

const isCalendarInAD = computed(() => {
  if (!store?.isCalendarInAD || props.dateType === 'bs') {
    return false
  } else {
    return true
  }
})

watch(date, (val) => {
  if (val === null && props.notRequired) {
  } else if (isCalendarInAD.value) {
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
    date.value = val ?? undefined
  },
)

const getDateValue = computed(() => {
  const convertedDate = DateConverter.getRepresentation(date.value, isCalendarInAD.value ? 'ad' : 'bs')
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
    return date >= props.toLimit.replaceAll('-', '/') || (date > '1944/04/13' && date < '2033/04/14')
  } else {
    return date > '1944/04/13' && date < '2033/04/14'
  }
}
</script>

<template>
  <div>
    <q-input
      class="full-width"
      debounce="1000"
      mask="####-##-##"
      type="text"
      :disable="props.disable"
      :error="!!props.error"
      :error-message="props.errorMessage"
      :hint="props.hint"
      :label="props.label"
      :model-value="getDateValue"
      :placeholder="props.placeholder"
      @on-click="select()"
      @update:model-value="onDateInput"
    >
      <template v-if="notRequired && !!getDateValue" #append>
        <q-icon class="cursor-pointer" name="close" @click="onDateInput('')" />
      </template>
    </q-input>
    <q-menu v-if="!props.disable" ref="menuRef" :no-focus="true">
      <q-date
        v-if="isCalendarInAD"
        v-model="date"
        mask="YYYY-MM-DD"
        :options="toDateValidation"
      />
      <BsDatePicker
        v-else
        v-model="date"
        :to-limit="props.toLimit"
        @close-menu="menuRef.hide()"
      />
    </q-menu>
  </div>
</template>
