<template>
  <q-page class="p-10">
    <div class="flex justify-between">
      <div class="flex gap-5">
        <n-auto-complete v-model="selectedBankAccount" :options="bankAccounts" endpoint="v1/bank-reconciliation/create-defaults" label="Bank Accounts" />
        <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
        <div>
          <q-btn icon="mdi-magnify" color="primary" label="Search" />
        </div>
      </div>
      <div>
        <q-btn icon="mdi-file-upload-outline" :disable="!selectedBankAccount || !startDate || !endDate ? true : false" color="green" label="Upload Statement" @click="statementPrompt = true"></q-btn>
      </div>
    </div>
    <q-dialog no-shake v-model="statementPrompt">
      <q-card style="min-width: 350px" class="p-5 space-y-3">
        <div class="text-xl text-gray-700 font-bold">
          Statement Upload
        </div>

        <n-auto-complete v-model="selectedBankAccount" :options="bankAccounts" endpoint="v1/bank-reconciliation/create-defaults" label="Bank Accounts" />
        <q-file bottom-slots v-model="model" label="Statement Document" counter max-files="1" accept=".csv, .xlsx" class="q-mb-md">
          <template v-slot:prepend>
            <q-icon name="cloud_upload" @click.stop.prevent />
          </template>
          <template v-slot:append>
            <q-icon v-if="model" name="close" @click.stop.prevent="model = null" class="cursor-pointer" />
          </template>

          <template v-slot:hint>
            <div class="text-gray-600">Upload your statement document here</div>
          </template>
        </q-file>

        <div>
          <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" id="modal-date-picker" />
          <div class="text-gray-600 -mt-4 text-xs">
            Please select the date range for the statement you are uploading (optional)
          </div>
        </div>

        <div class="text-right !mt-6">
          <q-btn label="Upload" color="green" @click="statementPrompt = false"></q-btn>
        </div>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
const selectedBankAccount = ref(null)
const bankAccounts = ref([])
const startDate = ref(null)
const endDate = ref(null)
const statementPrompt = ref(true)
const model = ref(null)

const endpoint = 'v1/bank-reconciliation/banks/'

useApi(endpoint).then((response) => {
  bankAccounts.value = response
})
</script>
