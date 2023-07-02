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
  }),
  getters: {
    doubleCount: (state) => state.counter * 2,
  },
  actions: {
    reset() {
      this.username = null
      this.email = null
      this.token = null
      this.companyInfo = null
      this.isCalendarInAD = true
      this.trialBalanceCollapseId = []
      this.stockTrialBalanceCollapseId = []
      this.userInfo = null
    },
  },
  persist: true,
})
