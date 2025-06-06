<script setup>
import DateConverter from 'src/components/date/VikramSamvat.js'
import checkPermissions from 'src/composables/checkPermissions'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'

const props = defineProps(['id'])
const store = useLoginStore()
const fields = ref(null)
const $q = useQuasar()
const route = useRoute()
const metaData = {
  title: 'Journal Voucher | Awecount',
}
const deleteMsg = ref(null)
const isDeleteOpen = ref(false)
const loading = ref(false)
const errors = ref(null)
useMeta(metaData)
const getData = () =>
  useApi(`/api/company/${route.params.company}/journal-voucher/${props.id || route.params.id}/`).then((data) => {
    fields.value = data
  })
getData()

const onCancelClick = () => {
  loading.value = true
  useApi(`/api/company/${route.params.company}/journal-voucher/${props.id || route.params.id}/cancel/`, {
    method: 'POST',
    body: { message: deleteMsg.value },
  })
    .then(() => {
      fields.value.status = fields.value?.status ? 'Cancelled' : ''
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
      fields.value.narration = `${fields.value.narration}` + `\nReason for cancellation: ${deleteMsg.value}`
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

<template>
  <div>
    <q-form autofocus class="q-pa-lg print-hide">
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
                <div class="col-6">
                  Voucher No
                </div>
                <div class="col-6">
                  {{ fields?.voucher_no || '-' }}
                </div>
              </div>
              <div class="col-6 row">
                <div class="col-6">
                  Date
                </div>
                <div class="col-6">
                  {{ store.isCalendarInAD ? fields?.date : DateConverter.getRepresentation(fields?.date, 'bs') }}
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-card>

      <q-card class="q-mt-sm overflow-y-auto">
        <q-card-section class="min-w-[650px]">
          <!-- Head -->
          <div class="row q-col-gutter-md text-grey-9">
            <div class="col-2">
              SN
            </div>
            <div class="col-2">
              Type
            </div>
            <div class="col-grow">
              Account
            </div>
            <div class="col-2">
              Dr Amount
            </div>
            <div class="col-2">
              Cr Amount
            </div>
          </div>

          <!-- Body -->
          <div v-for="(row, index) in fields?.rows" :key="row.id" class="q-my-md">
            <hr class="q-mb-md" />
            <div class="row q-col-gutter-md">
              <div class="col-2">
                {{ index + 1 }}
              </div>
              <div class="col-2">
                {{ row.type }}
              </div>
              <div class="col-grow">
                <router-link class="text-blue text-weight-medium" style="text-decoration: none" :to="`/${$route.params.company}/account/ledgers/${row.account_id}`">
                  {{ row.account_name }}
                </router-link>
              </div>
              <div class="col-2">
                <FormattedNumber type="currency" :value="row.dr_amount" />
              </div>
              <div class="col-2">
                <FormattedNumber type="currency" :value="row.cr_amount" />
              </div>
            </div>
          </div>

          <!-- Total -->
          <div class="row q-col-gutter-md text-bold q-mt-md">
            <div class="col-2"></div>
            <div class="col-2"></div>
            <div class="col-grow">
              Total
            </div>
            <div class="col-2">
              <FormattedNumber type="currency" :value="getTotalDrAmount" />
            </div>
            <div class="col-2">
              <FormattedNumber type="currency" :value="getTotalCrAmount" />
            </div>
          </div>
        </q-card-section>
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
      <div class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs">
        <div>
          <q-btn
            v-if="checkPermissions('journalvoucher.update') && fields?.status !== 'Cancelled'"
            class="text-h7 q-py-sm"
            color="orange"
            icon="edit"
            label="Edit"
            :to="`/${$route.params.company}/account/journal-vouchers/${props.id || route.params.id}/edit`"
          />
        </div>
        <div v-if="fields?.status === 'Approved' && checkPermissions('journalvoucher.cancel')">
          <q-btn
            class="text-h7 q-py-sm"
            color="red"
            icon="block"
            label="Cancel"
            @click.prevent="isDeleteOpen = true"
          />
        </div>
      </div>
    </q-form>
    <div class="print-only mt-1">
      <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif">
        <div>
          <h1 style="margin: 5px 0; font-size: 35px; font-weight: 500">
            {{ store?.companyInfo.name }}
          </h1>
          <div v-if="store?.companyInfo.address">
            {{ store?.companyInfo.address }}
          </div>
          <div v-if="store?.companyInfo.tax_identification_number">
            Tax Reg. No.
            <strong>{{ store.companyInfo.tax_identification_number }}</strong>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 5px; align-items: flex-end">
          <div style="margin-bottom: 5px">
            <img
              v-if="store?.companyInfo.logo_url"
              alt="Company Logo"
              style="height: 70px; max-width: 200px; object-fit: contain"
              :src="store?.companyInfo.logo_url"
            />
          </div>
          <div style="display: flex; align-items: center">
            <img alt="Email" src="/icons/telephone-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store?.companyInfo.contact_no }}</span>
          </div>
          <div v-if="store?.companyInfo?.emails?.length > 0" style="display: flex; align-items: center">
            <img alt="Call" src="/icons/envelope-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store?.companyInfo.emails && store.companyInfo.emails.length ? store.companyInfo.emails.join(',&nbsp;') : '' }}</span>
          </div>
        </div>
      </div>
      <hr style="margin: 20px 0" />
      <div class="text-center text-bold text-subtitle1 q-mb-md">
        Journal Voucher
      </div>
      <div class="row justify-between">
        <div>Date: {{ fields?.date || '-' }}</div>
        <div>J.V. No.: {{ fields?.voucher_no }}</div>
      </div>
      <table class="w-full text-center text-xs">
        <thead>
          <tr class="text-bold">
            <th class="col-one">
              SN
            </th>
            <th class="col-two">
              Type
            </th>
            <th class="col-three">
              Code
            </th>
            <th class="col-four">
              Account
            </th>
            <th class="col-five">
              Acc. Sheet No
            </th>
            <th class="col-six">
              Debit
            </th>
            <th class="col-seven">
              Credit
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in fields?.rows" :key="row.id" class="q-my-md">
            <td>{{ index + 1 }}</td>
            <td>{{ `${row.type} ` }}</td>
            <td>{{ row?.account_code }}</td>
            <td>
              <router-link :to="`/${$route.params.company}/account/ledgers/${row.account_id}`">
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
            <td colspan="5">
              Total
            </td>

            <td>{{ $nf(getTotalDrAmount) }}</td>
            <td>{{ $nf(getTotalCrAmount) }}</td>
          </tr>
        </tfoot>
      </table>

      <div v-if="fields?.narration" class="q-mt-xs narration">
        <span class="text-bold">Narration:&nbsp;</span>
        <span>{{ fields?.narration }}</span>
      </div>

      <div class="row q-mt-md">
        <div class="col" style="line-height: 160%">
          <div class="underline">
            Prepared By
          </div>
          <div>Name : {{ store?.userInfo.fullName }}</div>
          <div>Designation:</div>
          <div>Date : {{ today }}</div>
        </div>
        <div class="col" style="line-height: 160%">
          <div class="underline">
            Checked By
          </div>
          <div>Name:</div>
          <div>Designation:</div>
          <div>Date:</div>
        </div>

        <div class="col" style="line-height: 160%">
          <div class="underline">
            Approved By
          </div>
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
          <q-btn
            v-close-popup
            dense
            flat
            round
            class="text-red-700 bg-slate-200 opacity-95"
            icon="close"
          />
        </q-card-section>
        <q-card-section class="q-ma-md">
          <q-input
            v-model="deleteMsg"
            autofocus
            outlined
            type="textarea"
            :error="!!errors?.message"
            :error-message="errors?.message"
          />
          <div class="text-right q-mt-lg">
            <q-btn label="Confirm" @click="onCancelClick" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

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
