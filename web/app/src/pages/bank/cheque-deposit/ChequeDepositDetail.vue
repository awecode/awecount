<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span
            >Cheque Deposit | {{ fields?.status || '-' }} | #{{
              fields?.voucher_no || '-'
            }}</span
          >
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mt-none q-ml-lg q-mr-lg text-grey-8">
        <q-card-section>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">Bank Account</div>
              <div class="col-6">{{ fields?.bank_account_name || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">Benefactor</div>
              <div class="col-6">{{ fields?.benefactor_name || '-' }}</div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">Amount</div>
              <div class="col-6">{{ fields?.amount || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">Deposit Date</div>
              <div class="col-6">{{ getDate.deposit_date || '-' }}</div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">Cheque Date</div>
              <div class="col-6">{{ getDate.cheque_date || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">Cheque Number</div>
              <div class="col-6">{{ fields?.cheque_number || '-' }}</div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">Voucher Number</div>
              <div class="col-6">{{ fields?.voucher_no || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">Deposited By</div>
              <div class="col-6">{{ fields?.deposited_by || '-' }}</div>
            </div>
          </div>
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 row">
              <div class="col-6 text-bold">Clearing Date</div>
              <div class="col-6">{{ getDate.clearing_date || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6 text-bold">Drawee Bank</div>
              <div class="col-6">{{ fields?.drawee_bank || '-' }}</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <q-card class="q-mt-md" v-if="fields?.narration">
      <q-card-section>
        <div class="row">
          <div class="col-9 row text-grey-8">
            <div class="col-6">Narration</div>
            <div class="col-6">{{ fields?.narration || '-' }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <div class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs" v-if="fields">
      <div>
        <q-btn
          :to="`/bank/cheque/cheque-deposit/${id}/edit/`"
          color="orange"
          icon="edit"
          label="Edit"
          class="text-h7 q-py-sm"
        />
      </div>
      <div v-if="fields?.status === 'Issued'">
        <q-btn
          @click.prevent="onClearedClick"
          color="green"
          icon="done_all"
          label="Mark as cleared"
          class="text-h7 q-py-sm"
        />
      </div>
      <div v-if="fields?.status !== 'Cancelled'">
        <q-btn
          @click.prevent="() => (isDeleteOpen = true)"
          color="red"
          icon="block"
          label="Cancel"
          class="text-h7 q-py-sm"
        />
      </div>
      <div class="q-ml-auto" v-if="fields?.status === 'Cleared'">
        <q-btn
          :to="`/journal-entries/payment-receipt/${fields.id}/`"
          color="blue"
          icon="library_books"
          label="Journal Entries"
          class="text-h7 q-py-sm"
        />
      </div>
    </div>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6">
          <div class="text-h6 text-white">
            <span>Confirm Cancelation?</span>
          </div>
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-lg text-grey-8">
            <strong>Are you sure?</strong>
          </div>
          <div class="q-mx-xl text-blue">
            <div class="row justify-center">
              <q-btn class="q-mr-md" label="Yes" @click="cancel"></q-btn>
              <q-btn label="No" @click="() => (isDeleteOpen = false)"></q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script setup>
import useApi from 'src/composables/useApi'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
const store = useLoginStore()
const getDate = computed(() => {
  let dates = {
    deposit_date: DateConverter.getRepresentation(
      fields.value?.date,
      store.isCalendarInAD ? 'ad' : 'bs'
    ),
    clearing_date: DateConverter.getRepresentation(
      fields.value?.clearing_date,
      store.isCalendarInAD ? 'ad' : 'bs'
    ),
    cheque_date: DateConverter.getRepresentation(
      fields.value?.cheque_date,
      store.isCalendarInAD ? 'ad' : 'bs'
    ),
  }
  return dates
})
const props = defineProps(['id'])
const fields = ref(null)
const $q = useQuasar()
const isDeleteOpen = ref(false)
const getData = () =>
  useApi(`/v1/cheque-deposits/${props.id}/details/`).then((data) => {
    fields.value = data
  })
getData()

const onClearedClick = () => {
  useApi(`/v1/cheque-deposits/${props.id}/mark_as_cleared/`, {
    method: 'POST',
    body: {},
  })
    .then(() => {
      getData()
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
    })
    .catch(() => {
      $q.notify({
        color: 'negative',
        message: 'error',
        icon: 'report_problem',
      })
    })
}

const cancel = () => {
  useApi(`/v1/cheque-deposits/${props.id}/cancel/`, {
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
    })
    .catch(() => {
      $q.notify({
        color: 'negative',
        message: 'error',
        icon: 'report_problem',
      })
    })
}
</script>
