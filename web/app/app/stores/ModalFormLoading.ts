import { acceptHMRUpdate, defineStore } from 'pinia'

export const useModalFormLoading = defineStore('modalFormLoading', {
  state: () => ({}),
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useModalFormLoading, import.meta.hot))
}
