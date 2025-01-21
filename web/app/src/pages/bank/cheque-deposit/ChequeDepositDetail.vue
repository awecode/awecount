<script setup>
import DateConverter from 'src/components/date/VikramSamvat.js'
import checkPermissions from 'src/composables/checkPermissions'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'

const props = defineProps(['id'])
const loading = ref(false)
const store = useLoginStore()
const metaData = {
  title: 'Cheque Deposit View | Awecount',
}
useMeta(metaData)
const fields = ref(null)

const getDate = computed(() => {
  const dates = {
    deposit_date: DateConverter.getRepresentation(fields.value?.date, store.isCalendarInAD ? 'ad' : 'bs'),
    clearing_date: DateConverter.getRepresentation(fields.value?.clearing_date, store.isCalendarInAD ? 'ad' : 'bs'),
    cheque_date: DateConverter.getRepresentation(fields.value?.cheque_date, store.isCalendarInAD ? 'ad' : 'bs'),
  }
  return dates
})
const route = useRoute()
const $q = useQuasar()
const isDeleteOpen = ref(false)
const getData = async () =>
  await useApi(`/api/company/${route.params.company}/cheque-deposits/${props.id}/details/`, { method: 'GET' }, false, true).then((data) => {
    fields.value = data
  })
getData()

const onClearedClick = () => {
  loading.value = true
  useApi(`/api/company/${route.params.company}/cheque-deposits/${props.id}/mark_as_cleared/`, {
    method: 'POST',
    body: {},
  })
    .then(async () => {
      await getData()
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
      loading.value = false
    })
    .catch(() => {
      $q.notify({
        color: 'negative',
        message: 'error',
        icon: 'report_problem',
      })
      loading.value = false
    })
}

const onCancelClick = () => {
  loading.value = true
  useApi(`/api/company/${route.params.company}/cheque-deposits/${props.id}/cancel/`, {
    method: 'POST',
    body: {},
  })
    .then(() => {
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
      fields.value.status = 'Cancelled'
      isDeleteOpen.value = false
      loading.value = false
    })
    .catch(() => {
      $q.notify({
        color: 'negative',
        message: 'error',
        icon: 'report_problem',
      })
      loading.value = false
    })
}
</script>

<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Cheque Deposit | {{ fields?.status || '-' }} | #{{ fields?.id || '-' }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mt-none q-ml-lg q-mr-lg text-grey-8">
        <q-card-section>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Bank Account
              </div>
              <div class="col-6">
                {{ fields?.bank_account_name || '-' }}
              </div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Benefactor
              </div>
              <div class="col-6">
                {{ fields?.benefactor_name || '-' }}
              </div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Amount
              </div>
              <div class="col-6">
                {{ fields?.amount || '-' }}
              </div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Deposit Date
              </div>
              <div class="col-6">
                {{ getDate.deposit_date || '-' }}
              </div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Cheque Date
              </div>
              <div class="col-6">
                {{ getDate.cheque_date || '-' }}
              </div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Cheque Number
              </div>
              <div class="col-6">
                {{ fields?.cheque_number || '-' }}
              </div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Voucher Number
              </div>
              <div class="col-6">
                {{ fields?.voucher_no || '-' }}
              </div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Deposited By
              </div>
              <div class="col-6">
                {{ fields?.deposited_by || '-' }}
              </div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Clearing Date
              </div>
              <div class="col-6">
                {{ getDate.clearing_date || '-' }}
              </div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">
                Drawee Bank
              </div>
              <div class="col-6">
                {{ fields?.drawee_bank || '-' }}
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <q-card v-if="fields?.narration" class="q-mt-md">
      <q-card-section>
        <div class="row">
          <div class="col-9 row text-grey-8">
            <div class="col-6">
              Narration
            </div>
            <div class="col-6">
              {{ fields?.narration || '-' }}
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <div v-if="fields" class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs">
      <div v-if="checkPermissions('chequedeposit.modify')">
        <q-btn
          class="text-h7 q-py-sm"
          color="orange"
          icon="edit"
          label="Edit"
          :to="`/${$route.params.company}/banking/cheque-deposits/${props.id}/edit`"
        />
      </div>
      <div v-if="fields?.status === 'Issued' && checkPermissions('chequedeposit.modify')">
        <q-btn
          class="text-h7 q-py-sm"
          color="green"
          icon="done_all"
          label="Mark as cleared"
          :loading="loading"
          @click.prevent="onClearedClick"
        />
      </div>
      <div v-if="fields?.status !== 'Cancelled' && checkPermissions('chequedeposit.cancel')">
        <q-btn
          class="text-h7 q-py-sm"
          color="red"
          icon="block"
          label="Cancel"
          :loading="loading"
          @click.prevent="() => (isDeleteOpen = true)"
        />
      </div>
      <div v-if="fields?.status === 'Cleared'" class="q-ml-auto">
        <q-btn
          class="text-h7 q-py-sm"
          color="blue"
          icon="library_books"
          label="Journal Entries"
          :to="`/${$route.params.company}/journal-entries/cheque-deposits/${fields.id}`"
        />
      </div>
    </div>
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
                @click="onCancelClick"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
