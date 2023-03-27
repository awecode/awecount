import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginStore', {
  state: () => ({
    username: null,
    email: null,
    token: null,
    companyInfo: null,
    isCalendarInAD: true,
  }),
  getters: {
    doubleCount: (state) => state.counter * 2,
  },
  actions: {
    reset() {
      this.username = null
      this.email = null
      this.token = null
    },
  },
  persist: true,
})
