<script lang="ts">
import type { Ref } from 'vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import checkPermissions from 'src/composables/checkPermissions'
import numberToText from 'src/composables/numToText'
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import { useLoginStore } from 'src/stores/login-info'

interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  mode: string
  amount: number
  date: Date
}

export default {
  setup() {
    const route = useRoute()
    const metaData = {
      title: 'Payment Receipts | Awecount',
    }
    useMeta(metaData)
    const loginStore = useLoginStore()
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const isLoading = ref(false)
    const submitChangeStatus = (id: number, status: string) => {
      isLoading.value = true
      let endpoint = ''
      let body: null | object = null
      if (status === 'Cleared') {
        endpoint = `/api/company/${route.params.company}/payment-receipt/${id}/mark_as_cleared/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/api/company/${route.params.company}/payment-receipt/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
      }
      useApi(endpoint, body)
        .then(() => {
          // if (fields.value)
          if (fields.value) {
            fields.value.status = status
          }
          if (status === 'Cancelled') {
            isDeleteOpen.value = false
          }
          isLoading.value = false
        })
        .catch((err) => {
          console.log('err from the api', err)
          isLoading.value = false
        })
    }
    const getDate = computed(() => {
      return DateConverter.getRepresentation(fields.value?.date, 'bs')
    })
    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields,
      dialog: false,
      partyObj: null,
      modes,
      submitChangeStatus,
      isDeleteOpen,
      deleteMsg,
      modeOptions,
      numberToText,
      getDate,
      loginStore,
      checkPermissions,
      isLoading,
    }
  },
  created() {
    const endpoint = `/api/company/${this.$route.params.company}/payment-receipt/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' }, false, true)
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
}
</script>

<template>
  <div>
    <div class="print-only">
      <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif">
        <div>
          <h1 style="margin: 5px 0; font-size: 2rem; font-weight: 600; line-height: 2rem; margin-bottom: 1rem">
            {{ loginStore.companyInfo.name }}
            {{ loginStore.companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : 'Ltd.' }}
          </h1>
          <div v-if="loginStore.companyInfo.address">
            {{ loginStore.companyInfo.address }}
          </div>
          <div v-if="loginStore.companyInfo.tax_identification_number">
            Tax Reg. No.
            <strong>{{ loginStore.companyInfo.tax_identification_number }}</strong>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 5px; align-items: flex-end">
          <div style="margin-bottom: 5px">
            <img
              alt="Company Logo"
              style="height: 70px"
              :class="loginStore.companyInfo.logo_url ? '' : 'hidden'"
              :src="loginStore.companyInfo.logo_url"
            />
          </div>
          <div style="display: flex; align-items: center">
            <img alt="Email" src="/icons/telephone-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ loginStore.companyInfo.contact_no }}</span>
          </div>
          <div style="display: flex; align-items: center">
            <img alt="Call" src="/icons/envelope-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ loginStore.companyInfo.email }}</span>
          </div>
        </div>
      </div>
      <hr style="margin: 20px 0" />
      <div style="text-align: center">
        Payment Receipt | {{ fields?.status }}
      </div>
    </div>
    <div v-if="fields" class="sales-invoice">
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white print-hide">
          <div class="text-h6">
            <span>
              Payment Receipt | {{ fields?.status }}
              <span v-if="fields?.voucher_no">|</span>
            </span>
          </div>
        </q-card-section>
        <div class="q-pa-lg q-pb-lg">
          <div class="row justify-between">
            <span>
              <span class="text-weight-medium text-grey-8">Receipt ID:</span>
              {{ fields.id }}
            </span>
            <div class="row column items-end">
              <span>
                <span class="text-weight-medium text-grey-8">Date:</span>
                {{ fields.date }}
              </span>
              <span>
                <span class="text-weight-medium text-grey-8">Miti:</span>
                {{ getDate }}
              </span>
            </div>
          </div>
          <div class="row column q-mt-md q-gutter-y-sm">
            <span>
              <span class="text-weight-medium text-grey-8">Received from:</span>
              {{ fields.party_name }}
              <span v-if="fields.party_address">
                , {{ fields.party_address }}
              </span>
            </span>
            <span>
              <span class="text-weight-medium text-grey-8">Amount: </span>
              <FormattedNumber type="currency" :value="fields.amount" />
            </span>
            <span>
              <span class="text-weight-medium text-grey-8">In words:</span>
              {{ numberToText(Number(fields.amount)) }}
            </span>
          </div>
        </div>
      </q-card>
      <div v-if="fields.mode === 'Cheque'">
        <q-card class="q-mx-lg q-mb-sm">
          <q-card-section>
            <div class="row q-gutter-y-sm">
              <div class="col-md-6 col-12">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Mode:</span>
                    {{ fields.mode }}
                  </span>
                  <span>
                    <span class="text-weight-medium text-grey-8">Cheque Number:</span>
                    {{ fields.cheque_number }}
                  </span>
                </div>
              </div>
              <div class="col-md-6 col-12 row justify-between">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Drawee Bank:</span>
                    {{ fields.drawee_bank }}
                  </span>
                  <span>
                    <span class="text-weight-medium text-grey-8"></span>
                    Cheque Date: {{ fields.cheque_date }}
                  </span>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
        <q-card class="q-mx-lg q-mb-sm print-hide">
          <q-card-section>
            <div class="row q-gutter-y-sm q-gutter-x-lg">
              <div class="col-md-5 col-12">
                <div class="column q-gutter-y-sm">
                  <span class="row md-justify-between">
                    <span class="text-weight-medium text-grey-8">Debited Bank:</span>
                    {{ fields.bank_account_name }}
                  </span>
                  <span>
                    <span class="text-weight-medium text-grey-8">Clearing Date:</span>
                    {{ null }}
                  </span>
                </div>
              </div>
              <div class="col-md-5 col-12 row justify-between">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Voucher Number:</span>
                    {{ null }}
                  </span>
                  <!-- <span>
                  <span class="text-weight-medium text-grey-8"></span>
                  Cheque Date: {{ fields.cheque_date }}
                </span> -->
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div v-else-if="fields.mode === 'Cash'">
        <q-card class="q-mx-lg q-mb-sm">
          <q-card-section>
            <div class="row q-gutter-y-sm">
              <div class="col-md-6 col-12">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Mode:</span>
                    {{ fields.mode }}
                  </span>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div v-else>
        <q-card class="q-mx-lg q-mb-sm">
          <q-card-section>
            <div class="row q-gutter-y-sm">
              <div class="col-md-6 col-12">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Mode:</span>
                    {{ fields.mode }}
                  </span>
                </div>
              </div>
              <div class="col-md-6 col-12">
                <div class="column q-gutter-y-sm">
                  <span>
                    <span class="text-weight-medium text-grey-8">Bank:</span>
                    {{ fields.bank_account_name }}
                  </span>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <q-card class="q-mx-lg print-hide">
        <q-card-section>
          <div style="gap: 1px; display: flex; flex-direction: column; gap: 20px">
            <div class="row q-gutter-y-md">
              <div class="col-12 col-md-6 row">
                <span class="text-weight-medium col-6">Invoice #</span>
                <span>
                  <span v-for="invoice in fields.invoices" :key="invoice.id" class="col-6">
                    <router-link
                      v-if="checkPermissions('sales.read')"
                      class="text-blue q-mr-sm"
                      style="text-decoration: none"
                      :to="`/${$route.params.company}/sales/vouchers/${invoice.id}`"
                    >
                      #{{ invoice.id }}
                    </router-link>
                    <span v-else>#{{ invoice.id }}</span>
                  </span>
                </span>
              </div>
              <div class="col-12 col-md-6 row">
                <span class="text-weight-medium text-grey-8 col-6">Amount</span>
                <span>
                  <FormattedNumber type="currency" :value="fields.amount" />
                </span>
              </div>
            </div>
            <div class="row q-gutter-y-md">
              <div class="col-12 col-md-6 row">
                <span class="text-weight-medium text-grey-8 col-6">Status</span>
                <span>{{ fields.status }}</span>
              </div>
              <div class="col-12 col-md-6 row">
                <span class="text-weight-medium text-grey-8 col-6">TDS Amount</span>
                <span>
                  <FormattedNumber type="currency" :value="fields.tds_amount" />
                </span>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9">Remarks:</span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md">
        <div class="row q-gutter-x-sm q-mb-md print-hide">
          <span v-if="fields.status !== 'Cancelled'" class="row q-gutter-x-sm q-ml-none">
            <q-btn
              v-if="checkPermissions('paymentreceipt.update')"
              color="orange-7"
              icon="edit"
              label="Edit"
              :to="`/${$route.params.company}/payment-receipts/${fields.id}/edit`"
            />
            <q-btn
              v-if="fields.status !== 'Cleared' && checkPermissions('paymentreceipt.update')"
              color="green"
              icon="mdi-check-all"
              label="mark as cleared"
              :loading="isLoading"
              @click.prevent="() => submitChangeStatus(fields?.id, 'Cleared')"
            />
            <q-btn
              v-if="checkPermissions('paymentreceipt.cancel')"
              color="red"
              icon="cancel"
              label="cancel"
              :loading="isLoading"
              @click.prevent="() => (isDeleteOpen = true)"
            />
          </span>
        </div>
        <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end print-hide">
          <q-btn
            v-if="fields.mode === 'Cheque'"
            color="blue-7"
            icon="mdi-checkbook"
            label="View Cheque deposit"
            :to="`/${$route.params.company}/banking/cheque-deposits/${fields?.id}`"
          />
          <q-btn
            v-if="fields.status === 'Cleared'"
            color="blue-7"
            icon="books"
            label="Journal Entries"
            :to="`/${$route.params.company}/payment-receipts/${fields.id}/journal-entries`"
          />
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
                    @click="() => submitChangeStatus(fields?.id, 'Cancelled')"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </q-dialog>
      </div>
    </div>
    <div class="print-only text-right text-grey-9 text-caption">
      <div>Generated by {{ loginStore.username }} for {{ `${loginStore.companyInfo?.name}${loginStore.companyInfo.organization_type === 'private_limited' ? ' Pvt Ltd' : ''}` }}.</div>
      <div class="text-italic">
        This is a computer generated receipt, produced using awecount.com - IRD Approval No. 7600405
      </div>
    </div>
  </div>
</template>
