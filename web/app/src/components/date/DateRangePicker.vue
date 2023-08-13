<template>
  <div class="row q-col-gutter-md">
    <div class="row q-col-gutter-md target">
      <q-input :model-value="getText0" :error="error0" :error-message="errorMessage0" @update:model-value="onInput0"
        label="Start Date" />
      <q-input :model-value="getText1" :error="error1" :error-message="errorMessage1" @update:model-value="onInput1"
        label="End Date" />
    </div>
    <q-menu ref="menuDom" target=".target" :no-focus="true">
      <div class="row q-pa-md main-con">
        <div class="row" style="min-width: 150px">
          <div>
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
                <q-item-section @click="getMonth((last = false))">This Month</q-item-section>
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
        </div>
        <div v-if="isCalendarInAD" class="row md-no-wrap q-gutter-md date-Con">
          <q-date v-model="value0" mask="YYYY-MM-DD" />
          <q-date :options="toDateValidation" v-model="value1" mask="YYYY-MM-DD" />
        </div>
        <div v-else class="row md-no-wrap q-gutter-md date-Con">
          <bs-date-picker class="bs-date" v-model="value0"></bs-date-picker>
          <bs-date-picker v-model="value1" :toLimit="value0"></bs-date-picker>
        </div>
      </div>
    </q-menu>
    <!-- <div>
      <q-btn
        @click.prevent="filter"
        color="green"
        label="FILTER"
        class="q-mt-md"
      />
    </div> -->
    <div v-if="!props.hideBtns">
      <q-btn v-if="value0 || value1" color="red" icon="fa-solid fa-xmark " @click="clearFilter" class="q-mt-md" />
    </div>
  </div>
</template>

<script setup>
import BsDatePicker from '/src/components/date/BsDatePicker.vue'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
const store = useLoginStore()
const $q = useQuasar()

const props = defineProps(['startDate', 'endDate', 'hideBtns', 'focuOnMount'])

const menuDom = ref(null)
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

const emit = defineEmits(['update:startDate', 'update:endDate', 'filter'])
const clearFilter = () => {
  emit('update:startDate', null)
  emit('update:endDate', null)
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
//   emit('update:startDate', val)
// }
// const updated1 = (val) => {
//   emit('update:endDate', val)
// }

watch(
  () => value0.value,
  (val) => {
    emit('update:startDate', val)
  }
)
watch(
  () => value1.value,
  (val) => {
    emit('update:endDate', val)
  }
)

watch(
  () => props.startDate,
  (val) => {
    value0.value = val
  }
)
watch(
  () => props.endDate,
  (val) => {
    value1.value = val
  }
)

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
      emit('update:startDate', text)
    } else {
      error0.value = true
      errorMessage0.value = 'Invalid AD Date'
      // emit("update:startDate", "");
    }
  } else {
    if (DateConverter.isValid(text)) {
      emit('update:startDate', DateConverter.bs2ad(text))
    } else {
      error0.value = true
      errorMessage0.value = 'Invalid BS Date'
      // emit("update:startDate", "");
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
      emit('update:endDate', text)
    } else {
      error1.value = true
      errorMessage1.value = 'Invalid AD Date'
      // emit("update:endDate", "");
    }
  } else {
    if (DateConverter.isValid(text)) {
      emit('update:endDate', DateConverter.bs2ad(text))
    } else {
      error1.value = true
      errorMessage1.value = 'Invalid BS Date'
      // emit("update:endDate", "");
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
  emit('update:startDate', value)
  emit('update:endDate', value3)
  // active.value = false
}
const getYear = (last = false) => {
  const today = new Date()
  activeDate.value = last ? 'lastYear' : 'thisYear'
  if (isCalendarInAD.value) {
    let year = today.getFullYear()
    year = year - (last ? 1 : 0)
    setDateRange(buildDate(year, 1, 1), buildDate(year + 1, 1, 0))
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
  setDateRange(DateConverter.bs2ad(fy_start), DateConverter.bs2ad(fy_end))
}
const getMonth = (last = false) => {
  const today = new Date()
  const date = DateConverter.date2str(today)
  activeDate.value = last ? 'lastMonth' : 'thisMonth'
  if (isCalendarInAD.value) {
    let year = today.getFullYear()
    let month = today.getMonth() + 1
    month = month - (last ? 1 : 0)
    setDateRange(buildDate(year, month, 1), buildDate(year, month + 1, 0))
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
onMounted(() => {
  if (props.focuOnMount && (!value0.value && !value1.value)) {
    value0.value = store.dateRange.start_date
    value1.value = store.dateRange.end_date
    menuDom.value.show()
  }
})
watch([value0, value1], (newValve) => {
  store.updateDateRange(newValve[0], newValve[1])
})
const toDateValidation = (date) => {
  if (value0.value) {
    return date >= value0.value.replaceAll('-', '/')
  }
  else return true
}
</script>

<style>
.date-Con {
  width: 640px;
}

@media (max-width: 1280px) {
  .date-Con {
    width: 300px;
  }
}

@media (max-width: 520px) {
  .main-con {
    width: 325px;
  }
}

@media (min-width: 1280px) {
  .main-con {
    flex-wrap: nowrap;
  }
}
</style>
