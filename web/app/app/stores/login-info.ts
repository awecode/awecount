import { acceptHMRUpdate, defineStore } from 'pinia'

export const useLoginStore = defineStore(
  'login',
  () => {
    const auth = useAuth()

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
      await auth.logout()
    }

    const updateDateRange = (start_date: string, end_date: string) => {
      dateRange.value.start_date = start_date
      dateRange.value.end_date = end_date
    }

    const isLoggedIn = computed(() => {
      return auth.isAuthenticated.value
    })

    const username = computed(() => auth.user?.value?.full_name)
    const email = computed(() => auth.user?.value?.email)
    const token = computed(() => auth.token.value)
    const companyInfo = computed(() => ({
      ...auth.company.value,
      emails: [auth.company.value.email, auth.company.value.alternate_email].filter(Boolean),
      contact_no: [auth.company.value.phone, auth.company.value.alternate_phone].filter(Boolean).join(', '),
      logo_url: auth.company.value.logo,
    }))
    const userInfo = computed(() => auth.user.value)

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
