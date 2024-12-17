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
    <BankReconciliationTable v-if="systemTransactionData.length || statementTransactionData.length" :systemTransactionData="systemTransactionData" :statementTransactionData="statementTransactionData"
      :acceptableDifference="acceptableDifference" :adjustmentThreshold="adjustmentThreshold" />
  </q-page>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()

const selectedAccount = ref(route.query.account_id ? Number(route.query.account_id) : null)
const bankAccounts = ref([])
const startDate = ref(route.query.start_date as string || '2024-11-08')
const endDate = ref(route.query.end_date as string || '2024-12-08')
const systemTransactionData = ref([])
const statementTransactionData = ref([])
const acceptableDifference = ref(0.01)
const adjustmentThreshold = ref(1)

const endpoint = 'v1/bank-reconciliation/banks/'
const isLoading = ref(false)

useApi(endpoint).then((response) => {
  bankAccounts.value = response
})


const fetchTransactions = async () => {
  if (!selectedAccount.value || !startDate.value || !endDate.value) {
    return
  }
  isLoading.value = true
  router.push({
    query: {
      account_id: selectedAccount.value,
      start_date: startDate.value,
      end_date: endDate.value,
    }
  })
  systemTransactionData.value = []
  statementTransactionData.value = []

  useApi('v1/bank-reconciliation/unreconciled-transactions/?start_date=' + startDate.value + '&end_date=' + endDate.value + '&account_id=' + selectedAccount.value).then((response) => {
    systemTransactionData.value = response.system_transactions
    statementTransactionData.value = response.statement_transactions
    acceptableDifference.value = response.acceptable_difference
    adjustmentThreshold.value = response.adjustment_threshold
  }).catch((error) => {
    console.log(error)
    systemTransactionData.value = []
    statementTransactionData.value = []
  }).finally(() => {
    isLoading.value = false
  })
}

if (selectedAccount.value && startDate.value && endDate.value) {
  fetchTransactions()
}

</script>
