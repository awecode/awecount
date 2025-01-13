<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Fund Transfer</span>
          <span v-else>Update Fund Transfer</span>
        </div>
      </q-card-section>
      <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.voucher_no" label="Voucher No." class="col-12 col-md-6" :error-message="errors.voucher_no" :error="!!errors.voucher_no" />
            <date-picker v-model="fields.date" class="col-12 col-md-6" label="Date *" :error-message="errors.date" :error="!!errors.date"></date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2 v-model="fields.from_account" :options="formDefaults.collections?.from_account" endpoint="v1/fund-transfer/create-defaults/from_account/" :staticOption="fields.selected_from_account_obj" label="From Account *" :error="errors?.from_account" :disabled="!!fromAccount?.id" />
            </div>
            <div class="col-12 col-md-6">
              <n-auto-complete-v2 v-model="fields.to_account" :options="formDefaults.collections?.to_account" endpoint="v1/fund-transfer/create-defaults/to_account/" :staticOption="fields.selected_to_account_obj" label="To Account *" :error="errors?.to_account" />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.amount" label="Amount *" class="col-12 col-md-6" :error-message="errors.amount" :error="!!errors.amount" />
          </div>
          <div class="text-bold text-lg text-grey-8 q-mt-xl">Transaction Fees</div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2 v-model="fields.transaction_fee_account" endpoint="v1/fund-transfer/create-defaults/transaction_fee_account" :staticOption="fields.selected_transaction_fee_account_obj" :options="formDefaults.collections?.transaction_fee_account" label="Fees Account" :error="errors?.transaction_fee_account" />
            </div>
            <q-input v-model="fields.transaction_fee" label="Fees Amount" type="number" class="col-12 col-md-6" :error-message="errors.transaction_fee" :error="!!errors.transaction_fee" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn v-if="checkPermissions('FundTransferCreate') && !isEdit" @click.prevent="submitForm" color="green" :loading="loading" label="Create" type="submit" />
          <q-btn v-if="checkPermissions('FundTransferModify') && isEdit" @click.prevent="submitForm" color="green" :loading="loading" label="Update" type="submit" />
          <q-btn v-if="fields?.status == 'Issued' && checkPermissions('FundTransferCancel')" @click.prevent="isDeleteOpen = true" :loading="loading" icon="block" color="red" :label="'Cancel'" />
          <q-btn v-if="fields?.status == 'Issued'" :to="`/journal-entries/fund-transfer/${id}/`" color="blue" :loading="loading" icon="library_books" label="Journal Entries" class="text-h7 q-py-sm" />
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">Are you sure?</div>
          <div class="text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)"></q-btn>
              <q-btn flat class="text-red" label="Yes" @click="cancelForm"></q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script setup>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
const props = defineProps({
  fromAccount: {
    type: Object,
    required: false,
  },
  amount: {
    type: Number,
    required: false,
  },
  date: {
    type: String,
    required: false,
  },
  statementIds: {
    type: Array,
    required: false,
  },
  endpoint: {
    type: String,
    required: false,
  },
})

const fundTransferEndpoint = props.endpoint || '/v1/fund-transfer/'

const config = {
  getDefaults: true,
  successRoute: '/fund-transfer/list/',
}
if (props.endpoint) {
  config.createDefaultsEndpoint = '/v1/fund-transfer/create-defaults/'
}

const isDeleteOpen = ref(false)
const { fields, errors, isEdit, id, formDefaults, submitForm, cancelForm, loading, today } = useForm(fundTransferEndpoint, config)
const route = useRoute()
useMeta(() => {
  return {
    title: (isEdit?.value ? 'Update Funds Transfer' : 'Add Funds Transfer') + ' | Awecount',
  }
})

if (props.fromAccount) {
  fields.value.selected_from_account_obj = props.fromAccount
  fields.value.from_account = fields.value.from_account || Number(props.fromAccount.id)
}
if (props.amount) fields.value.amount = fields.value.amount || props.amount
if (props.date) fields.value.date = fields.value.date || props.date
else fields.value.date = fields.value.date || today
if (props.statementIds) fields.value.statement_ids = props.statementIds

onMounted(() => {
  if (route.params && route.params.template) {
    const template = route.params.template
    if (template.from_account) fields.value.from_account = template.from_account
    if (template.to_account) fields.value.to_account = template.to_account
    if (template.transaction_fee_account) fields.value.transaction_fee_account = template.transaction_fee_account
    if (template.transaction_fee) fields.value.transaction_fee = template.transaction_fee
  }
})
</script>
