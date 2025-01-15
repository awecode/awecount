<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { useRoute } from 'vue-router'
import useForm from '/src/composables/useForm'

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

const route = useRoute()

const fundTransferEndpoint = props.endpoint || `/api/company/${route.params.company}/fund-transfer/`

const config = {
  getDefaults: true,
  successRoute: `/${route.params.company}/banking/fund-transfers`,
}
if (props.endpoint) {
  config.createDefaultsEndpoint = `/api/company/${route.params.company}/fund-transfer/create-defaults/`
}

const isDeleteOpen = ref(false)
const { fields, errors, isEdit, id, formDefaults, submitForm, cancelForm, loading, today } = useForm(fundTransferEndpoint, config)

useMeta(() => {
  return {
    title: `${isEdit?.value ? 'Update Funds Transfer' : 'Add Funds Transfer'} | Awecount`,
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

<template>
  <q-form autofocus class="q-pa-lg">
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
            <q-input
              v-model="fields.voucher_no"
              class="col-12 col-md-6"
              label="Voucher No."
              :error="!!errors.voucher_no"
              :error-message="errors.voucher_no"
            />
            <date-picker
              v-model="fields.date"
              class="col-12 col-md-6"
              label="Date *"
              :error="!!errors.date"
              :error-message="errors.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.from_account"
                label="From Account *"
                :disabled="!!fromAccount?.id"
                :endpoint="`/api/company/${$route.params.company}/fund-transfer/create-defaults/from_account`"
                :error="errors?.from_account"
                :options="formDefaults.collections?.from_account"
                :static-option="fields.selected_from_account_obj"
              />
            </div>
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.to_account"
                label="To Account *"
                :endpoint="`/api/company/${$route.params.company}/fund-transfer/create-defaults/to_account`"
                :error="errors?.to_account"
                :options="formDefaults.collections?.to_account"
                :static-option="fields.selected_to_account_obj"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.amount"
              class="col-12 col-md-6"
              label="Amount *"
              :error="!!errors.amount"
              :error-message="errors.amount"
            />
          </div>
          <div class="text-bold text-lg text-grey-8 q-mt-xl">
            Transaction Fees
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.transaction_fee_account"
                label="Fees Account"
                :endpoint="`/api/company/${$route.params.company}/fund-transfer/create-defaults/transaction_fee_account`"
                :error="errors?.transaction_fee_account"
                :options="formDefaults.collections?.transaction_fee_account"
                :static-option="fields.selected_transaction_fee_account_obj"
              />
            </div>
            <q-input
              v-model="fields.transaction_fee"
              class="col-12 col-md-6"
              label="Fees Amount"
              type="number"
              :error="!!errors.transaction_fee"
              :error-message="errors.transaction_fee"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('fundtransfer.create') && !isEdit"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('fundtransfer.modify') && isEdit"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="fields?.status == 'Issued' && checkPermissions('fundtransfer.cancel')"
            color="red"
            icon="block"
            label="Cancel"
            :loading="loading"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="fields?.status == 'Issued'"
            class="text-h7 q-py-sm"
            color="blue"
            icon="library_books"
            label="Journal Entries"
            :loading="loading"
            :to="`/${$route.params.company}/journal-entries/fund-transfer/${id}/`"
          />
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn
            v-close-popup
            dense
            flat
            round
            class="text-red-700 bg-slate-200 opacity-95"
            icon="close"
          />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
            Are you sure?
          </div>
          <div class="text-blue">
            <div class="row justify-end">
              <q-btn
                flat
                class="q-mr-md text-blue-grey-9"
                label="NO"
                @click="() => (isDeleteOpen = false)"
              />
              <q-btn
                flat
                class="text-red"
                label="Yes"
                @click="cancelForm"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
