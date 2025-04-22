import { acceptHMRUpdate, defineStore } from 'pinia'

import { useAuthStore } from './auth'

export const useLoginStore = defineStore(
  'login',
  () => {
    const authStore = useAuthStore()

    const isCalendarInAD = ref<boolean>(true)
    const trialBalanceCollapseId = ref<string[]>([])
    const stockTrialBalanceCollapseId = ref<string[]>([])
    const chartOfAccountsExpandId = ref<string[]>([])
    const dateRange = ref<{
      start_date: string | null
      end_date: string | null
    }>({
      start_date: null,
      end_date: null,
    })

    const posData = ref<any>(null)
    const isFormLoading = ref<boolean>(false)

    const reset = async () => {
      await authStore.logout()
    }

    const updateDateRange = (start_date: string, end_date: string) => {
      dateRange.value.start_date = start_date
      dateRange.value.end_date = end_date
    }

    const isLoggedIn = computed(() => {
      return authStore.isAuthenticated
    })

    const username = computed(() => authStore.user?.full_name)
    const email = computed(() => authStore.user?.email)
    const token = computed(() => authStore.token)
    const companyInfo = computed(() => {
      return {
        ...authStore.company,
        emails: [authStore.company.email, authStore.company.alternate_email].filter(Boolean),
        contact_no: [authStore.company.phone, authStore.company.alternate_phone].filter(Boolean).join(', '),
        logo_url: authStore.company.logo,
      }
    })
    const userInfo = computed(() => authStore.user)

    return {
      username,
      email,
      token,
      companyInfo,
      userInfo,
      isCalendarInAD,
      trialBalanceCollapseId,
      stockTrialBalanceCollapseId,
      chartOfAccountsExpandId,
      posData,
      isFormLoading,
      isLoggedIn,
      dateRange,
      reset,
      updateDateRange,
    }
  },
  {
    persist: true,
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useLoginStore, import.meta.hot))
}
