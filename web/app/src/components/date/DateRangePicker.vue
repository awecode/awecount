<template>
  <div class="row q-col-gutter-md">
    <div class="row q-col-gutter-md target">
      <q-input :model-value="getText0" :error="error0" :error-message="errorMessage0" @update:model-value="onInput0" label="Start Date" />
      <q-input :model-value="getText1" :error="error1" :error-message="errorMessage1" @update:model-value="onInput1" label="End Date" />
    </div>
    <q-menu :target="'.target'" :no-focus="true">
      <div class=" row q-pa-md ">
        <div class="col-3" style="min-width: 200px">
          <div class="text-caption">Date Range</div>
          <q-list dense padding class="rounded-borders q-pr-md">
            <q-item clickable :active="activeDate == 'today'" v-ripple>
              <q-item-section @click="getToday((last = false))">Today</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'yesterday'" v-ripple>
              <q-item-section @click="getToday((last = true))">Yesterday</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'last7'" v-ripple>
              <q-item-section @click="getDays((last = 7))">Last 7 Days</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'last30'" v-ripple>
              <q-item-section @click="getDays((last = 30))">Last 30 Days</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'thisMonth'" v-ripple>
              <q-item-section @click="getMonth((last = false))">This
                Month</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'lastMonth'" v-ripple>
              <q-item-section @click="getMonth((last = true))">Last Month</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'thisYear'" v-ripple>
              <q-item-section @click="getYear((last = false))">This Year</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'lastYear'" v-ripple>
              <q-item-section @click="getYear((last = true))">Last Year</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'thisFY'" v-ripple>
              <q-item-section @click="getFY((last = false))">This FY</q-item-section>
            </q-item>
            <q-item clickable :active="activeDate == 'lastFY'" v-ripple>
              <q-item-section @click="getFY((last = true))">Last FY</q-item-section>
            </q-item>
          </q-list>
        </div>
        <div v-if="isCalendarInAD">
          <q-date class="col-6 q-mr-md" v-model="value0" mask="YYYY-MM-DD" />
          <q-date class="col-6" v-model="value1" mask="YYYY-MM-DD" />
        </div>
        <div v-else class="row ">
          <bs-date-picker class="q-mr-md" v-model="value0"></bs-date-picker>
          <bs-date-picker v-model="value1"></bs-date-picker>
        </div>
      </div>
    </q-menu>

    <div>
      <q-btn v-if="value0 || value1" color="red" icon="fa-solid fa-xmark " @click="clearFilter" class="q-mt-md" />
    </div>
    <div>
      <q-btn @click.prevent="filter" color="primary" label="FILTER" class="q-mt-md" />
    </div>

  </div>
</template>

<script setup>
import BsDatePicker from '/src/components/date/BsDatePicker.vue'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
const store = useLoginStore()
const $q = useQuasar()

const props = defineProps([
  'startDate',
  'endDate',
])

const value0 = ref(props.startDate)
const value1 = ref(props.endDate)
const error0 = ref(false)
const error1 = ref(false)
const errorMessage0 = ref('')
const errorMessage1 = ref('')
const activeDate = ref(null)

const isCalendarInAD = computed(() => {
  return store?.isCalendarInAD
})
// const showClear = computed(() => {
// return !this.hideClear && (this.value0 || this.value1)
// return false
// })

const emit = defineEmits(['updateStartDate', 'updateEndDate', 'filter'])
const clearFilter = () => {
  emit('updateStartDate', null)
  emit('updateEndDate', null)
  emit('filter')
}
const getText0 = computed(() => {
  // return value0.value
  return DateConverter.getRepresentation(
    value0.value,
    // this.$store.state.calendar
    isCalendarInAD.value ? 'ad' : 'bs'
  )
})
const getText1 = computed(() => {
  return DateConverter.getRepresentation(
    value1.value,
    // this.$store.state.calendar
    isCalendarInAD.value ? 'ad' : 'bs'
  )
})
// const updated0 = (val) => {
//   emit('updateStartDate', val)
// }
// const updated1 = (val) => {
//   emit('updateEndDate', val)
// }

watch(() => value0.value, (val) => {
  emit('updateStartDate', val)
})
watch(() => value1.value, (val) => {
  emit('updateEndDate', val)
})

watch(() => props.startDate, (val) => {
  value0.value = val
})
watch(() => props.endDate, (val) => {
  value1.value = val
})


const filter = () => {
  if (!value0.value && !value1.value) {
    $q.notify({
      color: 'negative',
      message: 'Date range is invalid',
      icon: 'report_problem',
    })
    return
  }
  emit('filter')
}


const onInput0 = (text) => {
  text = DateConverter.parseText(text)
  // if (!text) {
  //   return;
  // }
  error0.value = false
  errorMessage0.value = null
  if (isCalendarInAD.value) {
    if (DateConverter.isValidAD(text)) {
      emit('updateStartDate', text)
    } else {
      error0.value = true
      errorMessage0.value = 'Invalid AD Date'
      // emit("updateStartDate", "");
    }
  } else {
    if (DateConverter.isValid(text)) {
      emit('updateStartDate', DateConverter.bs2ad(text))
    } else {
      error0.value = true
      errorMessage0.value = 'Invalid BS Date'
      // emit("updateStartDate", "");
    }
  }
}
const onInput1 = (text) => {
  text = DateConverter.parseText(text)
  if (!text) {
    return
  }
  error1.value = false
  errorMessage1.value = null
  if (isCalendarInAD.value) {
    if (DateConverter.isValidAD(text)) {
      emit('updateEndDate', text)
    } else {
      error1.value = true
      errorMessage1.value = 'Invalid AD Date'
      // emit("updateEndDate", "");
    }
  } else {
    if (DateConverter.isValid(text)) {
      emit('updateEndDate', DateConverter.bs2ad(text))
    } else {
      error1.value = true
      errorMessage1.value = 'Invalid BS Date'
      // emit("updateEndDate", "");
    }
  }
}
// const parseCalendar = (val) => {
//   if (isCalendarInAD.value) return DateConverter.ad2bs(val)
//   return val
// }
const buildDate = (year, month, day) => {
  let date = new Date(year, month - 1, day)
  return DateConverter.date2str(date)
}
const setDateRange = (value, value3) => {
  emit('updateStartDate', value)
  emit('updateEndDate', value3)
  // active.value = false
}
const getYear = (last = false) => {
  const today = new Date()
  activeDate.value = last ? 'lastYear' : 'thisYear'
  if (isCalendarInAD.value) {
    let year = today.getFullYear()
    year = year - (last ? 1 : 0)
    setDateRange(
      buildDate(year, 1, 1),
      buildDate(year + 1, 1, 0)
    )
  } else {
    const date = DateConverter.date2str(today)
    let year = DateConverter.getBSYear(date)
    year = year - (last ? 1 : 0)
    const year_end_day = DateConverter.getMonthDays(year, 12)
    const bs0 = `${year}-01-01`
    const bs1 = `${year}-12-${year_end_day}`
    setDateRange(DateConverter.bs2ad(bs0), DateConverter.bs2ad(bs1))
  }
}
const getFY = (last = false) => {
  const today = new Date()
  const bs_month = DateConverter.getBSMonth(today)
  let bs_year = DateConverter.getBSYear(today)
  if (bs_month < 4) {
    bs_year = bs_year - 1
  }
  activeDate.value = last ? 'lastFY' : 'thisFy'
  bs_year = bs_year - (last ? 1 : 0)
  const fy_start = `${bs_year}-04-01`
  const fy_end = `${bs_year + 1}-03-${DateConverter.getMonthDays(
    bs_year + 1,
    3
  )}`
  setDateRange(
    DateConverter.bs2ad(fy_start),
    DateConverter.bs2ad(fy_end)
  )
}
const getMonth = (last = false) => {
  const today = new Date()
  const date = DateConverter.date2str(today)
  activeDate.value = last ? 'lastMonth' : 'thisMonth'
  if (isCalendarInAD.value) {
    let year = today.getFullYear()
    let month = today.getMonth() + 1
    month = month - (last ? 1 : 0)
    setDateRange(
      buildDate(year, month, 1),
      buildDate(year, month + 1, 0)
    )
  } else {
    let year = DateConverter.getBSYear(date)
    let month = DateConverter.getBSMonth(date)
    month = month - (last ? 1 : 0)
    const month_end_day = DateConverter.getMonthDays(year, month)
    const bs0 = `${year}-${month}-01`
    const bs1 = `${year}-${month}-${month_end_day}`
    setDateRange(DateConverter.bs2ad(bs0), DateConverter.bs2ad(bs1))
  }
}
const getToday = (last = false) => {
  activeDate.value = last ? 'yesterday' : 'today'
  const today = new Date()
  if (last) today.setDate(today.getDate() - 1)
  const date = DateConverter.date2str(today)
  setDateRange(date, date)
}
const getDays = (last = 7) => {
  const today = new Date()
  activeDate.value = last ? 'last' + last : null
  let startDay = new Date(today.getTime() - last * 86400000)
  const todayStr = DateConverter.date2str(today)
  const startDayStr = DateConverter.date2str(startDay)
  setDateRange(startDayStr, todayStr)
}
</script>
