<template>
  <q-page class="p-10">
    <div class="flex justify-between">
      <div class="flex gap-5">
        <n-auto-complete v-model="selectedAccount" :options="bankAccounts" label="Bank Accounts" optionValue="ledger_id" />
        <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
        <div>
          <q-btn :loading="isLoading" icon="mdi-magnify" color="primary" label="Search" @click="fetchTransactions" :disable="!selectedAccount || !startDate || !endDate ? true : false" />
        </div>
      </div>
      <div>
        <!-- <q-btn icon="mdi-file-upload-outline" color="green" label="Go to List" @click="router.push('/bank/reconciliation')" /> -->
      </div>
    </div>
    <ReconciliationTable v-if="accountDetails" :acceptableDifference="acceptableDifference" :adjustmentThreshold="adjustmentThreshold" :startDate="startDate" :endDate="endDate"
      :accountDetails="accountDetails" />
  </q-page>
</template>

<script setup lang="ts">
import { Ref } from 'vue'
const route = useRoute()
const router = useRouter()

type Bank = {
  ledger_id: number,
  id: number,
  cheque_no: string,
  account_number: string,
  name: string,
}

const selectedAccount = ref(route.query.account_id ? Number(route.query.account_id) : null)
const bankAccounts: Ref<Bank[]> = ref([])
const startDate = ref(route.query.start_date as string || '2024-11-08')
const endDate = ref(route.query.end_date as string || '2024-12-08')
const acceptableDifference = ref(0.01)
const adjustmentThreshold = ref(1)
const endpoint = 'v1/bank-reconciliation/defaults/'
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
    }
  })
  accountDetails.value = bankAccounts.value?.find((account) => account.ledger_id === selectedAccount.value) || null
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
