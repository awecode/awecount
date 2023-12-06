<template>
  <div class="">
    <div class="q-date q-date--portrait q-date--portrait-standard">
      <div class="q-date__header ">
        <div class="relative-position">
          <div class="q-date__header-subtitle q-date__header-link cursor-pointer" tabindex="0" @click="changeTo('year')">
            {{ year }}</div>
        </div>
        <div class="q-date__header-title relative-position flex no-wrap">
          <div class="relative-position col">
            <div class="q-date__header-title-label q-date__header-link q-date__header-link--active" tabindex="0"> {{
              weekDay }}, {{ months_list[month - 1] }} {{ day }}</div>
          </div>
        </div>
      </div>
      <div class="q-date__main col column" tabindex="-1">
        <div class="q-date__content col relative-position">
          <!------------------------ Calander ------------------------------------>
          <div v-if="!showMonth && !showYear" class="q-date__view q-date__calendar">
            <!------------------------------------------ Month, year switcher -------------------------------------->
            <div class="q-date__navigation row items-center no-wrap">
              <div class="row items-center q-date__arrow"><button
                  :disabled="(year < 2002 && month == 1) || disablePreviousBtns.month" @click="decMonth"
                  class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--round q-btn--actionable q-focusable q-hoverable q-btn--dense"
                  tabindex="0" type="button" style="font-size: 10px;"><span class="q-focus-helper"></span><span
                    class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                      class="q-icon" aria-hidden="true" role="img"><svg viewBox="0 0 24 24">
                        <path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"></path>
                      </svg></span></span></button></div>
              <div class="relative-position overflow-hidden flex flex-center col">
                <div><button @click="changeTo('month')"
                    class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--rectangle q-btn--actionable q-focusable q-hoverable q-btn--no-uppercase q-btn--dense"
                    tabindex="0" type="button"><span class="q-focus-helper"></span><span
                      class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                        class="block">{{ months_list[month
                          - 1] }}</span></span></button></div>
              </div>
              <div class="row items-center q-date__arrow"><button :disabled="year == 2089 && month == 12"
                  @click="incMonth"
                  class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--round q-btn--actionable q-focusable q-hoverable q-btn--dense"
                  tabindex="0" type="button" style="font-size: 10px;"><span class="q-focus-helper"></span><span
                    class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                      class="q-icon" aria-hidden="true" role="img"><svg viewBox="0 0 24 24">
                        <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"></path>
                      </svg></span></span></button></div>
              <div class="row items-center q-date__arrow"><button :disabled="year < 2002 || disablePreviousBtns.year"
                  @click="decYear"
                  class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--round q-btn--actionable q-focusable q-hoverable q-btn--dense"
                  tabindex="0" type="button" style="font-size: 10px;"><span class="q-focus-helper"></span><span
                    class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                      class="q-icon" aria-hidden="true" role="img"><svg viewBox="0 0 24 24">
                        <path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"></path>
                      </svg></span></span></button></div>
              <div class="relative-position overflow-hidden flex flex-center">
                <div><button @click="changeTo('year')"
                    class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--rectangle q-btn--actionable q-focusable q-hoverable q-btn--no-uppercase q-btn--dense q-btn--active"
                    tabindex="0" type="button"><span class="q-focus-helper"></span><span
                      class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                        class="block">{{ year
                        }}</span></span></button></div>
              </div>
              <div class="row items-center q-date__arrow"><button :disabled="!(year < 2089)" @click="incYear"
                  class="q-btn q-btn-item non-selectable no-outline q-btn--flat q-btn--round q-btn--actionable q-focusable q-hoverable q-btn--dense"
                  tabindex="0" type="button" style="font-size: 10px;"><span class="q-focus-helper"></span><span
                    class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                      class="q-icon" aria-hidden="true" role="img"><svg viewBox="0 0 24 24">
                        <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"></path>
                      </svg></span></span></button></div>
            </div>

            <!-- ------------------------------Days heading --------------------------->
            <div class="q-date__calendar-weekdays row items-center no-wrap">
              <div class="q-date__calendar-item" v-for="day in days_list" :key=day>
                <div>{{ day.slice(0, 3) }}</div>
              </div>
            </div>
            <!-------------------------------------- Days listing--------------------------------- -->
            <div class="q-date__calendar-days-container relative-position overflow-hidden">
              <div class="q-date__calendar-days fit">
                <span v-for="(row, index) in monthRows" :key="index">
                  <span v-for="(obj, j) in row" :key="j">
                    <span class="border-none" v-if="obj" @click="onDateClick(obj)">
                      <div class="q-date__calendar-item q-date__calendar-item--in"><button :disabled="compareBsDate(obj)"
                          class="day-selector q-btn q-btn-item non-selectable no-outline q-btn--rectangle q-btn--actionable q-focusable q-hoverable q-btn--dense"
                          tabindex="0"
                          :class="day == obj ? 'q-btn--unelevated bg-primary text-white' : 'q-btn--flat q-btn--active'"
                          type="button"><span class="q-focus-helper" :tabindex="day == obj ? '-1' : '0'"></span><span
                            class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                              class="block">{{ obj
                              }}</span></span></button></div>
                    </span>
                    <span v-else>
                      <div class="q-date__calendar-item q-date__calendar-item--fill">
                        <div></div>
                      </div>
                    </span>
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- ----------------------------------------------------Month listing----------------------------------- -->
          <div v-if="showMonth" class="q-date__view q-date__years flex flex-center justify-between row  flex-center">
            <span v-for="monthList, index in months_list" :key="monthList" class="col-4"
              @click="month = (index + 1), showMonth = false">
              <div class="q-date__months-item flex flex-center"><button
                  class="q-btn q-btn-item non-selectable no-outline  q-btn--rectangle text-null q-btn--actionable q-focusable q-hoverable"
                  :class="month == (index + 1) ? 'q-btn--unelevated bg-primary text-white' : 'q-btn--flat text-null'"
                  tabindex="0" type="button"><span class="q-focus-helper"></span><span
                    class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                      class="block">{{ monthList
                      }}</span></span></button>
              </div>
            </span>
          </div>

          <!------------------------------------ Years listing------------------------------- -->
          <div v-if="showYear" class="q-date__view q-date__years flex flex-center">
            <div class="q-date__years-content col self-stretch row items-center">
              <div v-for="i in 22" :key="i" class="col-3" @click="year = i + 2068, showYear = false">
                <div class="q-date__years-item flex flex-center "><button
                    class="q-btn q-btn-item non-selectable no-outline  q-btn--rectangle  q-btn--actionable q-focusable q-hoverable q-btn--dense"
                    :class="i + 2068 == year ? 'q-btn--unelevated bg-primary text-white q-btn--active' : 'q-btn--flat  text-null '"
                    tabindex="0" type="button"><span class="q-focus-helper"></span><span
                      class="q-btn__content text-center col items-center q-anchor--skip justify-center row"><span
                        class="block">{{ i + 2068 }}</span></span></button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import DateConverter from './VikramSamvat'
const props = defineProps(['modelValue', 'error', 'toLimit'])
const emit = defineEmits(['update:modelValue'])
const ad_date = ref(props.modelValue || null)
if (!ad_date.value) {
  ad_date.value = DateConverter.date2str(new Date())
}
const showMonth = ref(false)
const showYear = ref(false)
// const years_list = DateConverter.getYears()
const months_list = DateConverter.getMonths()
const days_list = DateConverter.getDays()

const converted_bs_date = ref(DateConverter.ad2bs(ad_date.value))

const year = ref(null)
const month = ref(null)
const day = ref(null)
if (converted_bs_date.value) {
  [year.value, month.value, day.value] = converted_bs_date.value
    .split('-')
    .map(data => parseInt(data))
}

const bsDate = computed(() => {
  if (year.value && month.value && day.value) {
    return `${year.value}-${month.value}-${day.value}`
  }
  return ''
})

const adDate = computed(() => {
  return DateConverter.bs2ad(bsDate.value)
})

const weekDay = computed(() => {
  return DateConverter.getDays()[new Date(adDate.value).getDay()].substring(
    0,
    3
  )
})

const monthStartDay = computed(() => {
  let bs_month_start_date_in_ad = new Date(
    DateConverter.bs2ad(`${year.value}-${month.value}-${1}`)
  )
  return bs_month_start_date_in_ad.getDay() + 1
})

const monthDays = computed(() => {
  return DateConverter.getMonthDays(year.value, month.value)
})

const monthRows = computed(() => {
  let rows = []
  let date = 1
  let first_row = true
  do {
    let new_row = []
    for (let i = 1; i <= 7; i++) {
      if (first_row) {
        if (i < monthStartDay.value) {
          new_row.push('')
        } else {
          new_row.push(date)
          date = date + 1
        }
      } else {
        if (date <= monthDays.value) {
          new_row.push(date)
          date = date + 1
        } else {
          new_row.push('')
        }
      }
    }
    first_row = false
    rows.push(new_row)
  } while (date <= monthDays.value)
  return rows
})

watch(() => props.modelValue, (newVal) => {
  let converted_bs_date1 = DateConverter.ad2bs(newVal)
  if (converted_bs_date1) {
    let [year_second, month_second, day_second] = converted_bs_date1
      .split('-')
      .map(data => parseInt(data))
    year.value = year_second
    month.value = month_second
    day.value = day_second
  }
})

watch(() => bsDate.value, (newVal) => {
  let modVal = DateConverter.bs2ad(newVal, true)
  emit('update:modelValue', modVal)
})

const onDateClick = (data) => {
  if (!props.modelValue && bsDate.value) {
    emit('update:modelValue', DateConverter.bs2ad(bsDate.value))
  }
  if (props.toLimit) {
    const selectedDate = `${year.value}-${month.value < 10 ? `0${month.value}` : `${month.value}`}-${data < 10 ? `0${data}` : `${data}`}`
    const toLimitConverted = DateConverter.ad2bs(props.toLimit)
    if (selectedDate >= toLimitConverted) {
      day.value = data
    }
  }
  else day.value = data
}
const compareBsDate = (day) => {
  if (props.toLimit) {
    const selectedDate = `${year.value}-${month.value < 10 ? `0${month.value}` : `${month.value}`}-${day < 10 ? `0${day}` : `${day}`}`
    const toLimitConverted = DateConverter.ad2bs(props.toLimit)
    return !(selectedDate >= toLimitConverted)
  }
  else return false
}

const incMonth = () => {
  if (month.value > 11) {
    month.value = 1
    year.value = year.value + 1
  } else {
    month.value = month.value + 1
    // if (!day.value) {
    //   day.value - 1
    // }
  }
}

const decMonth = () => {
  if (month.value < 2) {
    month.value = 12
    year.value = year.value - 1
  } else {
    month.value = month.value - 1
  }
}

const incYear = () => {
  if (year.value < 2090)
    year.value = year.value + 1
}

const decYear = () => {
  year.value = year.value - 1
}

const changeTo = (time) => {
  if (time == 'year') {
    showMonth.value = false
    if (showYear.value == true) {
      showYear.value = false
    }
    else {
      showYear.value = true
    }
  }
  else if (time == 'month') {
    showMonth.value = true
    showYear.value = false
  }
  else {
    showMonth.value = false
    showYear.value = false
  }
}
const disablePreviousBtns = computed(() => {
  const data = {
    year: false,
    month: false
  }
  if (props.toLimit) {
    const toLimitConverted = DateConverter.ad2bs(props.toLimit)
    const limitMonth = toLimitConverted.split('-')[1]
    const limitYear = toLimitConverted.split('-')[0]

    if (limitYear >= year.value) {
      data.year = true
      if (limitMonth >= month.value) data.month = true
    }
  }
  return data
})
</script>

<style scoped>
button.day-selector:disabled {
  opacity: 0.3 !important;
}
</style>
