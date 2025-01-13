<template>
  <div>
    <q-form class="q-pa-lg print-hide" autofocus>
      <q-card>
        <q-card-section class="bg-green text-white">
          <div class="text-h6">
            <span>
              Journal Voucher | #{{ fields?.voucher_no || '-' }} |
              {{ fields?.status || '-' }}
            </span>
          </div>
        </q-card-section>

        <q-card class="q-mt-none q-ml-lg q-mr-lg text-grey-8">
          <q-card-section>
            <div class="grid md:grid-cols-2 q-col-gutter-md q-mb-sm">
              <div class="col-6 row">
                <div class="col-6">Voucher No</div>
                <div class="col-6">{{ fields?.voucher_no || '-' }}</div>
              </div>
              <div class="col-6 row">
                <div class="col-6">Date</div>
                <div class="col-6">{{ store.isCalendarInAD ? fields?.date : DateConverter.getRepresentation(fields?.date, 'bs') }}</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-card>

      <q-card class="q-mt-sm overflow-y-auto">
        <q-card-section class="min-w-[650px]">
          <!-- Head -->
          <div class="row q-col-gutter-md text-grey-9">
            <div class="col-2">SN</div>
            <div class="col-2">Type</div>
            <div class="col-grow">Account</div>
            <div class="col-2">Dr Amount</div>
            <div class="col-2">Cr Amount</div>
          </div>

          <!-- Body -->
          <div v-for="(row, index) in fields?.rows" :key="row.id" class="q-my-md">
            <hr class="q-mb-md" />
            <div class="row q-col-gutter-md">
              <div class="col-2">{{ index + 1 }}</div>
              <div class="col-2">{{ row.type }}</div>
              <div class="col-grow">
                <router-link class="text-blue text-weight-medium" style="text-decoration: none" :to="`/account/${row.account_id}/view/`">{{ row.account_name }}</router-link>
              </div>
              <div class="col-2">{{ row.dr_amount || 0 }}</div>
              <div class="col-2">{{ row.cr_amount || 0 }}</div>
            </div>
          </div>

          <!-- Total -->
          <div class="row q-col-gutter-md text-bold q-mt-md">
            <div class="col-2"></div>
            <div class="col-2"></div>
            <div class="col-grow">Total</div>
            <div class="col-2">
              {{ $nf(getTotalDrAmount) }}
            </div>
            <div class="col-2">
              {{ $nf(getTotalCrAmount) }}
            </div>
          </div>
        </q-card-section>
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
      <div class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs">
        <div>
          <q-btn v-if="checkPermissions('JournalVoucherModify') && fields?.status !== 'Cancelled'" :to="`/journal-voucher/${props.id}/edit/`" color="orange" icon="edit" label="Edit" class="text-h7 q-py-sm" />
        </div>
        <div v-if="fields?.status == 'Approved' && checkPermissions('JournalVoucherCancel')">
          <q-btn @click.prevent="isDeleteOpen = true" color="red" icon="block" label="Cancel" class="text-h7 q-py-sm" />
        </div>
      </div>
    </q-form>
    <div class="print-only mt-1">
      <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif">
        <div>
          <h1 style="margin: 5px 0; font-size: 35px; font-weight: 500">{{ store?.companyInfo.name }}</h1>
          <div>{{ store?.companyInfo.address }}</div>
          <div>
            Tax Reg. No.
            <strong>{{ store.companyInfo.tax_registration_number }}</strong>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 5px; align-items: flex-end">
          <div style="margin-bottom: 5px">
            <img v-if="store?.companyInfo.logo_url" :src="store?.companyInfo.logo_url" alt="Compony Logo" style="height: 70px; max-width: 200px; object-fit: contain" />
          </div>
          <div style="display: flex; align-items: center">
            <img src="/icons/telephone-fill.svg" alt="Email" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store?.companyInfo.contact_no }}</span>
          </div>
          <div style="display: flex; align-items: center" v-if="store?.companyInfo?.emails?.length > 0">
            <img src="/icons/envelope-fill.svg" alt="Call" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store?.companyInfo.emails && store.companyInfo.emails.length ? store.companyInfo.emails.join(',&nbsp;') : '' }}</span>
          </div>
        </div>
      </div>
      <hr style="margin: 20px 0" />
      <div class="text-center text-bold text-subtitle1 q-mb-md">Journal Voucher</div>
      <div class="row justify-between">
        <div>Date: {{ fields?.date || '-' }}</div>
        <div>J.V. No.: {{ fields?.voucher_no }}</div>
      </div>
      <table class="w-full text-center text-xs">
        <thead>
          <tr class="text-bold">
            <th class="col-one">SN</th>
            <th class="col-two">Type</th>
            <th class="col-three">Code</th>
            <th class="col-four">Account</th>
            <th class="col-five">Acc. Sheet No</th>
            <th class="col-six">Debit</th>
            <th class="col-seven">Credit</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in fields?.rows" :key="row.id" class="q-my-md">
            <td>{{ index + 1 }}</td>
            <td>{{ row.type + ' ' }}</td>
            <td>{{ row?.account_code }}</td>
            <td>
              <router-link :to="`/account/${row.account_id}/view/`">
                {{ row.account_name }}
              </router-link>
            </td>
            <td>{{ row.account_id }}</td>
            <td>{{ row.dr_amount || '-' }}</td>
            <td>{{ row.cr_amount || '-' }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="text-bold q-mt-md">
            <td colspan="5">Total</td>

            <td>{{ $nf(getTotalDrAmount) }}</td>
            <td>{{ $nf(getTotalCrAmount) }}</td>
          </tr>
        </tfoot>
      </table>

      <div class="q-mt-xs narration" v-if="fields?.narration">
        <span class="text-bold">Narration:&nbsp;</span>
        <span>{{ fields?.narration }}</span>
      </div>

      <div class="row q-mt-md">
        <div class="col" style="line-height: 160%">
          <div class="underline">Prepared By</div>
          <div>Name : {{ store?.userInfo.fullName }}</div>
          <div>Designation:</div>
          <div>Date : {{ today }}</div>
        </div>
        <div class="col" style="line-height: 160%">
          <div class="underline">Checked By</div>
          <div>Name:</div>
          <div>Designation:</div>
          <div>Date:</div>
        </div>

        <div class="col" style="line-height: 160%">
          <div class="underline">Approved By</div>
          <div>Name:</div>
          <div>Designation:</div>
          <div>Date:</div>
        </div>
      </div>
    </div>
    <q-dialog v-model="isDeleteOpen" @before-hide="errors = {}">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6 flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-ma-md">
          <q-input autofocus v-model="deleteMsg" type="textarea" outlined :error="!!errors?.message" :error-message="errors?.message"></q-input>
          <div class="text-right q-mt-lg">
            <q-btn label="Confirm" @click="onCancelClick"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
import checkPermissions from 'src/composables/checkPermissions'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
const store = useLoginStore()
const props = defineProps(['id'])
const fields = ref(null)
const $q = useQuasar()
const metaData = {
  title: 'Journal Voucher | Awecount',
}
const deleteMsg = ref(null)
const isDeleteOpen = ref(false)
const loading = ref(false)
const errors = ref(null)
useMeta(metaData)
const getData = () =>
  useApi(`/v1/journal-voucher/${props.id}/`).then((data) => {
    fields.value = data
  })
getData()

const onCancelClick = () => {
  loading.value = true
  useApi(`/v1/journal-voucher/${props.id}/cancel/`, {
    method: 'POST',
    body: { message: deleteMsg.value },
  })
    .then(() => {
      fields.value?.status ? (fields.value.status = 'Cancelled') : ''
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
      fields.value.narration = `${fields.value.narration}` + ('\nReason for cancellation: ' + deleteMsg.value)
      loading.value = false
      isDeleteOpen.value = false
    })
    .catch((err) => {
      const parsedError = useHandleFormError(err)
      errors.value = parsedError.errors
      $q.notify({
        color: 'negative',
        message: parsedError.message,
        icon: 'report_problem',
      })
      loading.value = false
    })
}

// function prompt() {
//   $q.dialog({
//     title: 'Confirm Cancelation?',
//     message: 'Reason for cancelation?',
//     prompt: {
//       model: '',
//       type: 'text', // optional
//     },
//     cancel: true,
//     persistent: true,
//   })
//     .onOk((data) => {
//       cancel(data)
//     })
//     .onCancel(() => {
//       // console.log('>>>> Cancel')
//     })
//     .onDismiss(() => {
//       // console.log('I am triggered on both OK and Cancel')
//     })
// }
const getTotalCrAmount = computed(() => fields.value?.rows?.reduce((accum, item) => accum + Number(item.cr_amount), 0) || 0)

const getTotalDrAmount = computed(() => fields.value?.rows?.reduce((accum, item) => accum + Number(item.dr_amount), 0) || 0)
const today = DateConverter.getRepresentation(new Date().toISOString().slice(0, 10), store.isCalendarInAD ? 'ad' : 'bs')
</script>

<style scoped>
@media print {
  .q-card {
    box-shadow: none;
    border: 1px solid gray;
    border-radius: 0;
  }

  .q-markup-table,
  .q-markup-table {
    box-shadow: none;
  }

  hr {
    margin: 0px;
  }

  .q-col-gutter-y-md > *,
  .q-col-gutter-md > * {
    padding: 0px;
  }

  .q-col-gutter-y-md,
  .q-col-gutter-md {
    margin-top: 0px;
    padding: 8px 20px;
  }

  .q-my-md {
    margin-top: 0px;
    margin-bottom: 0px;
  }

  a {
    text-decoration: none;
    color: black;
  }

  .q-card__section--vert {
    padding: 10px 16px;
  }

  .narration {
    border: none;
    border-radius: 0;
    box-shadow: none;
  }

  .narration-selection-card {
    padding: 0;
  }

  .underline {
    text-underline-offset: 0.3em;
    text-decoration: underline;
  }

  .col-one,
  .col-two {
    width: 10% !important;
  }

  .col-three {
    width: 12%;
  }

  .col-four {
    width: 27% !important;
  }

  .col-five {
    width: 17% !important;
  }

  .col-six,
  .col-seven {
    width: 12% !important;
  }
}

.col-one,
.col-two,
.col-three {
  width: 12%;
}

.col-four {
  width: 34%;
}

.col-five {
  width: 0%;
}

.col-six,
.col-seven {
  width: 15%;
}

table,
th,
td {
  border: 1px solid black;
  border-collapse: collapse;
}

td {
  padding: 3px;
}
</style>
