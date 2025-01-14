<script setup>
import BsDatePicker from 'src/components/date/BsDatePicker.vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

const props = defineProps(['startDate', 'endDate', 'hideBtns', 'focusOnMount'])

// const showClear = computed(() => {
// return !this.hideClear && (this.value0 || this.value1)
// return false
// })

const emit = defineEmits(['update:startDate', 'update:endDate', 'filter'])

const store = useLoginStore()

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
    isCalendarInAD.value ? 'ad' : 'bs',
  )
})
const getText1 = computed(() => {
  return DateConverter.getRepresentation(
    value1.value,
    // this.$store.state.calendar
    isCalendarInAD.value ? 'ad' : 'bs',
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
  },
)
watch(
  () => value1.value,
  (val) => {
    emit('update:endDate', val)
  },
)

watch(
  () => props.startDate,
  (val) => {
    value0.value = val
  },
)
watch(
  () => props.endDate,
  (val) => {
    value1.value = val
  },
)

// const filter = () => {
//   if (!value0.value && !value1.value) {
//     $q.notify({
//       color: 'negative',
//       message: 'Date range is invalid',
//       icon: 'report_problem',
//     })
//     return
//   }
//   emit('filter')
// }

const onInput0 = (text) => {
  text = DateConverter.parseText(text)
  if (!text) {
    return
  }
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
  const date = new Date(year, month - 1, day)
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
  let fy_start
  let fy_end
  if (store.companyInfo.config_template === 'np') {
    const bs_month = DateConverter.getBSMonth(today)
    let bs_year = DateConverter.getBSYear(today)
    if (bs_month < 4) {
      bs_year = bs_year - 1
    }
    bs_year = bs_year - (last ? 1 : 0)
    const bs_start = `${bs_year}-04-01`
    const bs_end = `${bs_year + 1}-03-${DateConverter.getMonthDays(bs_year + 1, 3)}`
    fy_start = DateConverter.bs2ad(bs_start)
    fy_end = DateConverter.bs2ad(bs_end)
  } else {
    const ad_month = today.getMonth()
    let ad_year = today.getFullYear()
    if (ad_month < 9) {
      ad_year = ad_year + 1
    }
    ad_year = ad_year - (last ? 1 : 0)
    fy_start = `${ad_year}-10-01`
    fy_end = `${ad_year + 1}-09-30`
  }
  activeDate.value = last ? 'lastFY' : 'thisFY'
  setDateRange(fy_start, fy_end)
}
const getMonth = (last = false) => {
  const today = new Date()
  const date = DateConverter.date2str(today)
  activeDate.value = last ? 'lastMonth' : 'thisMonth'
  if (isCalendarInAD.value) {
    const year = today.getFullYear()
    let month = today.getMonth() + 1
    month = month - (last ? 1 : 0)
    setDateRange(buildDate(year, month, 1), buildDate(year, month + 1, 0))
  } else {
    let year = DateConverter.getBSYear(date)
    let month = DateConverter.getBSMonth(date)
    month = month - (last ? 1 : 0)
    if (last && month == 0) {
      month = 12
      year = year - 1
    }
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
  activeDate.value = last ? `last${last}` : null
  const startDay = new Date(today.getTime() - last * 86400000)
  const todayStr = DateConverter.date2str(today)
  const startDayStr = DateConverter.date2str(startDay)
  setDateRange(startDayStr, todayStr)
}
onMounted(() => {
  if (props.focusOnMount && !value0.value && !value1.value) {
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
    return date >= value0.value.replaceAll('-', '/') && date < '2033/04/16'
  } else {
    return date < '2033/04/16'
  }
}
</script>

<template>
  <div class="flex gap-x-4 gap-y-2">
    <div class="flex gap-x-6 gap-y-0 target">
      <q-input
        debounce="1000"
        label="Start Date"
        mask="####-##-##"
        :error="error0"
        :error-message="errorMessage0"
        :model-value="getText0"
        @update:model-value="onInput0"
      />
      <q-input
        debounce="1000"
        label="End Date"
        mask="####-##-##"
        :error="error1"
        :error-message="errorMessage1"
        :model-value="getText1"
        @update:model-value="onInput1"
      />
    </div>
    <q-menu ref="menuDom" target=".target" :no-focus="true">
      <div class="row q-pa-md main-con">
        <div class="row" style="min-width: 150px">
          <div>
            <div class="text-caption">
              Date Range
            </div>
            <q-list dense padding class="rounded-borders q-pr-md">
              <q-item v-ripple clickable :active="activeDate == 'today'">
                <q-item-section
                  @click="
                    getToday((last = false))
                    menuDom.hide()
                  "
                >
                  Today
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'yesterday'">
                <q-item-section
                  @click="
                    getToday((last = true))
                    menuDom.hide()
                  "
                >
                  Yesterday
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'last7'">
                <q-item-section
                  @click="
                    getDays((last = 7))
                    menuDom.hide()
                  "
                >
                  Last 7 Days
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'last30'">
                <q-item-section
                  @click="
                    getDays((last = 30))
                    menuDom.hide()
                  "
                >
                  Last 30 Days
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'thisMonth'">
                <q-item-section
                  @click="
                    getMonth((last = false))
                    menuDom.hide()
                  "
                >
                  This Month
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'lastMonth'">
                <q-item-section
                  @click="
                    getMonth((last = true))
                    menuDom.hide()
                  "
                >
                  Last Month
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'thisYear'">
                <q-item-section
                  @click="
                    getYear((last = false))
                    menuDom.hide()
                  "
                >
                  This Year
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'lastYear'">
                <q-item-section
                  @click="
                    getYear((last = true))
                    menuDom.hide()
                  "
                >
                  Last Year
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'thisFY'">
                <q-item-section
                  @click="
                    getFY((last = false))
                    menuDom.hide()
                  "
                >
                  This FY
                </q-item-section>
              </q-item>
              <q-item v-ripple clickable :active="activeDate == 'lastFY'">
                <q-item-section
                  @click="
                    getFY((last = true))
                    menuDom.hide()
                  "
                >
                  Last FY
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>
        <div v-if="isCalendarInAD" class="row md-no-wrap q-gutter-md date-Con">
          <div>
            <div class="mb-2 text-base font-medium text-gray-600">
              From
            </div>
            <q-date v-model="value0" mask="YYYY-MM-DD" :options="(date) => date < '2033/04/16'" />
          </div>
          <div>
            <div class="mb-2 text-base font-medium text-gray-600">
              To
            </div>
            <q-date v-model="value1" mask="YYYY-MM-DD" :options="toDateValidation" />
          </div>
        </div>
        <div v-else class="row md-no-wrap q-gutter-md date-Con">
          <div>
            <div class="mb-2 text-base font-medium text-gray-600">
              From
            </div>
            <BsDatePicker v-model="value0" class="bs-date" />
          </div>
          <div>
            <div class="mb-2 text-base font-medium text-gray-600">
              To
            </div>
            <BsDatePicker v-model="value1" :to-limit="value0" />
          </div>
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
      <q-btn
        v-if="value0 || value1"
        class="q-mt-md"
        color="red"
        icon="fa-solid fa-xmark "
        @click="clearFilter"
      />
    </div>
  </div>
</template>

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
