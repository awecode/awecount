import { acceptHMRUpdate, defineStore } from 'pinia'

export const useLoginStore = defineStore('login', {
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
      start_date: null,
      end_date: null,
    },
    posData: null,
    isFormLoading: false,
  }),
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
    },
  },
  persist: true,
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useLoginStore, import.meta.hot))
}
