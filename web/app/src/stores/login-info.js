import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginStore', {
  state: () => ({
    username: null,
    email: null,
    token: null,
    companyInfo: null,
    isCalendarInAD: true,
    trialBalanceCollapseId: [],
    stockTrialBalanceCollapseId: [],
    userInfo: null,
    dateRange: {
      start_date : null,
      end_date: null
    }
  }),
  getters: {
    doubleCount: (state) => state.counter * 2,
  },
  actions: {
    reset() {
      this.username = null
      this.email = null
      this.token = null
      this.companyInfo = {}
      this.userInfo = {}
    },
    updateDateRange(start_date, end_date) {
      this.dateRange.start_date = start_date
      this.dateRange.end_date = end_date
    }
  },
  persist: true,
})
