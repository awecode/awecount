// A module to convert Bikram Samwat [B.S.] to A.D. and vice versa.
// Range:
// 1944 A.D. to 2033 A.D.
// 2000 B.S. to 2089 B.S.
// bs : a dictionary that contains the number of days in each month of the B.S. year
// bs_equiv, ad_equiv  : The B.S. and A.D. equivalent dates for counting and calculation

const BS_EQIV = '2000-09-17'
const AD_EQIV = '1944-01-01'

const bs = {}
bs[2000] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2001] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2002] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2003] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2004] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2005] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2006] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2007] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2008] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31]
bs[2009] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2010] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2011] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2012] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30]
bs[2013] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2014] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2015] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2016] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30]
bs[2017] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2018] = [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2019] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2020] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2021] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2022] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
bs[2023] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2024] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2025] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2026] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2027] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2028] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2029] = [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30]
bs[2030] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2031] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2032] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2033] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2034] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2035] = [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31]
bs[2036] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2037] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2038] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2039] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30]
bs[2040] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2041] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2042] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2043] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30]
bs[2044] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2045] = [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2046] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2047] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2048] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2049] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
bs[2050] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2051] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2052] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2053] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
bs[2054] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2055] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2056] = [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30]
bs[2057] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2058] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2059] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2060] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2061] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2062] = [30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31]
bs[2063] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2064] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2065] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2066] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31]
bs[2067] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2068] = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2069] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2070] = [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30]
bs[2071] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2072] = [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30]
bs[2073] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31]
bs[2074] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2075] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2076] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
bs[2077] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2078] = [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2079] = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
bs[2080] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
bs[2081] = [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31]
bs[2082] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30]
bs[2083] = [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30]
bs[2084] = [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30]
bs[2085] = [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30]
bs[2086] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30]
bs[2087] = [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30]
bs[2088] = [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30]
bs[2089] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30]
// bs[2090] = [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30]

var _MS_PER_DAY = 1000 * 60 * 60 * 24

function dateDiffInDays(a, b) {
  // Discard the time and time-zone information.
  var utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate())
  var utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate())

  return Math.floor((utc2 - utc1) / _MS_PER_DAY)
}

const Converter = {
  countBsDays: function (begin_bs_date, end_bs_date) {
    // Returns the number of days between the two given B.S. dates.
    // begin_ad_date : A tuple in the format (year,month,day) that specify the date to start counting from.
    // end_ad_date : A tuple in the format (year,month,day) that specify the date to end counting.
    // NOTE:
    // Tuple in the dictionary starts from 0
    // The range(a,b) function starts from a and ends at b-1

    let [begin_year, begin_month, begin_day] = begin_bs_date
      .split('-')
      .map((data) => parseInt(data))
    let [end_year, end_month, end_day] = end_bs_date
      .split('-')
      .map((data) => parseInt(data))

    let days = 0

    // 1) First add total days in all the years
    for (let year = begin_year; year < end_year + 1; year++) {
      for (let days_in_month of bs[year]) {
        days = days + days_in_month
      }
    }
    // 2) Subtract the days from first (n-1) months of the beginning year
    for (let month = 0; month < begin_month; month++) {
      days = days - bs[begin_year][month]
    }
    // 3) Add the number of days from the last month of the beginning year
    days = days + bs[begin_year][12 - 1]

    // 4) Subtract the days from the last months from the end year
    for (let month = end_month - 1; month < 12; month++) {
      days = days - bs[end_year][month]
    }

    // 5) Add the beginning days excluding the day itself
    days = days - begin_day - 1

    // 5) Add the last remaining days excluding the day itself
    days = days + end_day - 1
    return days
  },

  countAdDays: function (begin_ad_date, end_ad_date) {
    // Returns the number of days between the two given A.D. dates.
    // begin_ad_date : A tuple in the format (year,month,day) that specify the date to start counting from.
    // end_ad_date : A tuple in the format (year,month,day) that specify the date to end counting.
    let date_begin = new Date(begin_ad_date)
    let date_end = new Date(end_ad_date)

    return dateDiffInDays(date_begin, date_end)
  },

  addAdDays: function (ad_date, num_days) {
    // Adds the given number of days to the given A.D. date and returns it as a tuple in the format (year,month,day)
    // ad_date : A tuple in the format (year,month,day)
    // num_days : Number of days to add to the given date
    let date = new Date(ad_date)
    date.setDate(date.getDate() + num_days)
    return `${date.getFullYear()}-${this.zeroPad(
      date.getMonth() + 1
    )}-${this.zeroPad(date.getDate())}`
  },

  addBsDays: function (bs_date, num_days) {
    // Adds the given number of days to the given B.S. date and returns it as a tuple in the format (year,month,day)
    // bs_date : a tuple in the format (year,month,day)
    // num_days : Number of days to add to the given date
    // Note:
    // Tuple in the dictionary starts from 0

    let [year, month, day] = bs_date.split('-').map((data) => parseInt(data))

    // 1) Add the total number of days to the original days
    day = day + num_days

    // 2) Until the number of days becomes applicable to the current month,
    // subtract the days by the number of days in the current month and increase the month

    // try {
    while (day > bs[year][month - 1]) {
      day = day - bs[year][month - 1]
      month = month + 1
      if (month > 12) {
        month = 1
        year = year + 1
      }
    }
    // } catch (e) {

    // }

    return `${year}-${this.zeroPad(month)}-${this.zeroPad(day)}`
  },

  zeroPad: function (num) {
    var zero = 2 - num.toString().length + 1
    return Array(+(zero > 0 && zero)).join('0') + num
  },

  bs2ad: function (bs_date, roundOff) {
    // input and output in string
    if (this.isValid(bs_date)) {
      let date_delta = this.countBsDays(BS_EQIV, bs_date)
      return this.addAdDays(AD_EQIV, date_delta)
    } else {
      if (roundOff) {
        let dateArray = bs_date.split('-')
        let day = Number(bs_date.split('-')[2])
        let dateString = bs_date
        do {
          day -= 1
          dateArray[2] = dateArray[2] - 1
          dateString = dateArray.join('-')
        } while (day > 28 && !this.isValid(dateString))
        if (this.isValid(dateString)) {
          let date_delta = this.countBsDays(BS_EQIV, dateString)
          return this.addAdDays(AD_EQIV, date_delta)
        } else throw 'Invalid BS Date'
      } else throw 'Invalid BS Date'
    }
  },

  ad2bs: function (ad_date) {
    let dt = new Date(ad_date)
    if (dt != 'Invalid Date') {
      let date_delta = this.countAdDays(AD_EQIV, ad_date)
      return this.addBsDays(BS_EQIV, date_delta)
    }
    // } catch (e) {
    //     throw 'invalid date'
    // }
    // if non-empty throw error
    if (ad_date) {
      console.error(ad_date)
      throw 'invalid date'
    } else {
      ad_date = 'null'
    }
  },

  getBSYear: function (ad_date) {
    let bs_date = this.ad2bs(ad_date)
    return parseInt(bs_date.split('-')[0])
  },

  getBSMonth: function (ad_date) {
    let bs_date = this.ad2bs(ad_date)
    return parseInt(bs_date.split('-')[1])
  },
  isValidAD: function (date_as_str) {
    return (
      date_as_str.length > 7 &&
      !isNaN(Date.parse(date_as_str)) &&
      isNaN(date_as_str) &&
      Date.parse(date_as_str) > -8520356476000 && // after 1699-12-12
      !(date_as_str.length == 8 && date_as_str.endsWith('-'))
    )
  },

  isValid: function (date_as_str) {
    // """
    // Checks if the fed date string is a valid B.S. date
    // date_as_str: String in the format 'YYYY-MM-DD'
    // Returns True for valid date, False for invalid.
    // """
    let [year, month, day] = [null, null, null]
    try {
      ;[year, month, day] = date_as_str.split('-').map((data) => parseInt(data))
    } catch (e) {
      return false
    }
    if (!(month > 0 && month < 13)) {
      return false
    }
    try {
      if (!(day > 0 && day <= bs[year][month - 1])) {
        return false
      }
    } catch (e) {
      throw `The year ${year} is not supported`
    }
    return true
  },

  parseText(text) {
    if (text.length > 10) {
      // Remove extra zero in 2020-01-014
      if (text.substr(-3, 1) == '0') {
        text = text.substr(0, text.length - 3) + text.substr(-2)
        // } else {
        //   return;
      }
    }
    return text
  },

  getMonthDays(year, month) {
    try {
      return bs[year][month - 1]
    } catch (e) {
      throw `BS ${year} not supported.`
    }
  },
  getYears() {
    // exclude 2000
    return Object.keys(bs).slice(1).reverse()
  },

  getMonths() {
    return [
      'Baishakh',
      'Jestha',
      'Asadh',
      'Shrawan',
      'Bhadra',
      'Ashwin',
      'Kartik',
      'Mangsir',
      'Poush',
      'Magh',
      'Falgun',
      'Chaitra',
    ]
  },

  getDays() {
    return [
      'Sunday',
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
    ]
  },

  getRepresentation(adDate, calendarType, showTime = false) {
    if (typeof adDate === 'undefined' || adDate === null || adDate === '') {
      return
    }
    let time = new Date(adDate + ' GMT').toUTCString().slice(-12, -4)
    if (calendarType === 'ad' && time !== '00:00:00') {
      let dateStr = new Date(adDate).toISOString().slice(0, 10)
      if (showTime) {
        dateStr += dateStr + ' ' + time
      }
      return dateStr
    }
    if (calendarType === 'bs' && time !== '00:00:00' && showTime) {
      return this.ad2bs(adDate) + ' ' + time
    } else if (calendarType === 'bs') {
      return this.ad2bs(adDate)
    } else {
      try {
        return new Date(adDate + ' GMT').toISOString().substr(0, 10)
      } catch (err) {
        if (err.message == 'invalid date') {
          return new Date(adDate).toISOString().substr(0, 10)
        }
        console.error(err)
      }
    }
  },
  date2str(date) {
    return `${date.getFullYear()}-${this.zeroPad(
      date.getMonth() + 1
    )}-${this.zeroPad(date.getDate())}`
  },
}

export default Converter
