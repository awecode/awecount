<script setup lang="ts">
import type { Ref } from 'vue'

const route = useRoute()
const router = useRouter()

interface Bank {
  ledger_id: number
  id: number
  cheque_no: string
  account_number: string
  name: string
}

const selectedAccount = ref(route.query.account_id ? Number(route.query.account_id) : null)
const bankAccounts: Ref<Bank[]> = ref([])
const startDate = ref(route.query.start_date as string)
const endDate = ref(route.query.end_date as string)
const acceptableDifference = ref(0.01)
const adjustmentThreshold = ref(1)
const endpoint = `/api/company/${route.params.company}/bank-reconciliation/defaults/`
const isLoading = ref(false)
const accountDetails: Ref<Bank | null> = ref(null)

const fetchTransactions = async () => {
  if (!selectedAccount.value || !startDate.value || !endDate.value) {
    return
  }
  await nextTick()
  router.push({
    query: {
      account_id: selectedAccount.value,
      start_date: startDate.value,
      end_date: endDate.value,
    },
  })
  accountDetails.value = bankAccounts.value?.find(account => account.ledger_id === selectedAccount.value) || null
}

useApi(endpoint).then((response) => {
  bankAccounts.value = response.banks
  acceptableDifference.value = response.acceptable_difference
  adjustmentThreshold.value = response.adjustment_threshold

  if (selectedAccount.value && startDate.value && endDate.value) {
    fetchTransactions()
  }
})
</script>

<template>
  <q-page class="p-10">
    <div class="flex justify-between">
      <div class="flex gap-5">
        <n-auto-complete
          v-model="selectedAccount"
          label="Bank Accounts"
          option-value="ledger_id"
          :options="bankAccounts"
        />
        <DateRangePicker v-model:end-date="endDate" v-model:start-date="startDate" :hide-btns="true" />
        <div>
          <q-btn
            color="primary"
            icon="mdi-magnify"
            label="Search"
            :disable="!selectedAccount || !startDate || !endDate ? true : false"
            :loading="isLoading"
            @click="fetchTransactions"
          />
        </div>
      </div>
      <div>
        <!-- <q-btn icon="mdi-file-upload-outline" color="green" label="Go to List" @click="router.push('/bank/reconciliation')" /> -->
      </div>
    </div>
    <ReconciliationTable
      v-if="accountDetails"
      :acceptable-difference="acceptableDifference"
      :account-details="accountDetails"
      :adjustment-threshold="adjustmentThreshold"
      :end-date="endDate"
      :start-date="startDate"
    />
  </q-page>
</template>
