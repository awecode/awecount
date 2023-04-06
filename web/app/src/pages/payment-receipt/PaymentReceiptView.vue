<template>
  <div v-if="fields" class="sales-invoice">
    <q-card class="q-ma-lg q-mb-sm">
      <q-card-section class="bg-green text-white">
        <div class="text-h6 d-print-none">
          <span>Payment Receipt | Issued</span>
        </div>
      </q-card-section>

      <div class="q-ma-lg q-pb-lg">
        <div class="row justify-between">
          <span
            ><span class="text-weight-medium text-grey-8">Receipt ID: </span>
            {{ fields.id }}</span
          >
          <div class="row column items-end">
            <span
              ><span class="text-weight-medium text-grey-8">Date: </span
              >{{ fields.date }}</span
            >
            <span>
              <span class="text-weight-medium text-grey-8">Miti: </span>
              {{ getDate }}</span
            >
          </div>
        </div>
        <div class="row column q-mt-md q-gutter-y-sm">
          <span
            ><span class="text-weight-medium text-grey-8">Received from: </span>
            {{ fields.party_name }}, {{ fields.party_address }}</span
          >
          <span
            ><span class="text-weight-medium text-grey-8">Amount: </span> NRS
            {{ fields.amount }}</span
          >
          <span
            ><span class="text-weight-medium text-grey-8">In words: </span>
            {{ numberToText(fields.amount) }}</span
          >
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
                  <span class="text-weight-medium text-grey-8">Mode: </span>
                  {{ fields.mode }}</span
                >
                <span>
                  <span class="text-weight-medium text-grey-8"
                    >Cheque Number:
                  </span>
                  {{ fields.cheque_number }}</span
                >
              </div>
            </div>
            <div class="col-md-6 col-12 row justify-between">
              <div class="column q-gutter-y-sm">
                <span>
                  <span class="text-weight-medium text-grey-8"
                    >Drawee Bank:
                  </span>
                  {{ fields.drawee_bank }}</span
                >
                <span>
                  <span class="text-weight-medium text-grey-8"></span>
                  Cheque Date: {{ fields.cheque_date }}
                </span>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <q-card class="q-mx-lg q-mb-sm">
        <q-card-section>
          <div class="row q-gutter-y-sm q-gutter-x-lg">
            <div class="col-md-5 col-12">
              <div class="column q-gutter-y-sm">
                <span class="row md-justify-between">
                  <span class="text-weight-medium text-grey-8"
                    >Debited Bank:
                  </span>
                  {{ fields.bank_account_name }}</span
                >
                <span>
                  <span class="text-weight-medium text-grey-8"
                    >Clearing Date:
                  </span>
                  {{ null }}</span
                >
              </div>
            </div>
            <div class="col-md-5 col-12 row justify-between">
              <div class="column q-gutter-y-sm">
                <span>
                  <span class="text-weight-medium text-grey-8"
                    >Voucher Number:
                  </span>
                  {{ null }}</span
                >
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
                  <span class="text-weight-medium text-grey-8">Mode: </span>
                  {{ fields.mode }}</span
                >
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
                  <span class="text-weight-medium text-grey-8">Mode: </span>
                  {{ fields.mode }}</span
                >
              </div>
            </div>
            <div class="col-md-6 col-12">
              <div class="column q-gutter-y-sm">
                <span>
                  <span class="text-weight-medium text-grey-8">Bank: </span>
                  {{ fields.bank_account_name }}</span
                >
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
    <q-card class="q-mx-lg">
      <q-card-section>
        <div style="gap: 1px; display: flex; flex-direction: column; gap: 20px">
          <div class="row q-gutter-y-md">
            <div class="col-12 col-md-6 row">
              <span class="text-weight-medium col-6">Invoice #</span>
              <span>
                <span
                  class="col-6"
                  v-for="invoice in fields.invoices"
                  :key="invoice.id"
                >
                  <router-link
                    class="text-blue q-mr-sm"
                    style="text-decoration: none"
                    :to="`/sales-voucher/${invoice.id}/view`"
                    >#{{ invoice.id }}</router-link
                  >
                </span>
              </span>
            </div>
            <div class="col-12 col-md-6 row">
              <span class="text-weight-medium text-grey-8 col-6">Amount</span>
              <span>Rs. {{ fields.amount }}</span>
            </div>
          </div>
          <div class="row q-gutter-y-md">
            <div class="col-12 col-md-6 row">
              <span class="text-weight-medium text-grey-8 col-6">Status</span>
              <span>{{ fields.status }}</span>
            </div>
            <div class="col-12 col-md-6 row">
              <span class="text-weight-medium text-grey-8 col-6">
                TDS Amount</span
              >
              <span>{{ fields.tds_amount }}</span>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <q-card class="q-mx-lg q-my-md" v-if="fields?.remarks">
      <q-card-section>
        <span class="text-subtitle2 text-grey-9"> Remarks: </span>
        <span class="text-grey-9">{{ fields?.remarks }}</span>
      </q-card-section>
    </q-card>
    <div
      class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none"
      v-if="fields"
    >
      <div class="row q-gutter-x-sm q-mb-md">
        <q-btn
          color="orange-7"
          label="Edit"
          icon="edit"
          :to="`/payment-receipt/${fields.id}/`"
        />
        <span
          v-if="fields.status !== 'Cancelled'"
          class="row q-gutter-x-sm q-ml-none"
        >
          <q-btn
            v-if="fields.status !== 'Cleared'"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Cleared')"
            color="green"
            label="mark as cleared"
            icon="mdi-check-all"
          />
          <q-btn
            @click.prevent="() => (isDeleteOpen = true)"
            color="red"
            label="cancel"
            icon="cancel"
          />
        </span>
      </div>
      <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end">
        <q-btn
          v-if="fields.mode === 'Cheque'"
          color="blue-7"
          label="View Cheque deposit"
          icon="mdi-checkbook"
          :to="`/bank/cheque/cheque-deposit/${fields?.id}/view/`"
        />
        <q-btn
          v-if="fields.status === 'Cleared'"
          color="blue-7"
          label="Journal Entries"
          icon="books"
          :to="`/journal-entries/payment-receipt/${fields?.id}/`"
        />
      </div>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6">
            <div class="text-h6 text-white">
              <span>Confirm Cancelation?</span>
            </div>
          </q-card-section>

          <q-card-section>
            <div class="q-mb-lg text-grey-8">
              <strong>Are you sure?</strong>
            </div>
            <div class="q-mx-xl text-blue">
              <div class="row justify-center">
                <q-btn
                  class="q-mr-md"
                  label="Yes"
                  @click="() => submitChangeStatus(fields?.id, 'Cancelled')"
                ></q-btn>
                <q-btn label="No" @click="() => (isDeleteOpen = false)"></q-btn>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </div>
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import { Ref } from 'vue'
import numberToText from 'src/composables/numToText'
import DateConverter from '/src/components/date/VikramSamvat.js'
interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  mode: string
  amount: number
}
export default {
  setup() {
    const metaData = {
      title: 'Payment Receipts | Awecount',
    }
    useMeta(metaData)
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const submitChangeStatus = (id: number, status: string) => {
      let endpoint = ''
      let body: null | object = null
      if (status === 'Cleared') {
        endpoint = `/v1/payment-receipt/${id}/mark_as_cleared/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/v1/payment-receipt/${id}/cancel/`
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
        })
        .catch((err) => console.log('err from the api', err))
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
      modes: modes,
      submitChangeStatus,
      isDeleteOpen,
      deleteMsg,
      modeOptions,
      numberToText,
      getDate,
    }
  },
  created() {
    const endpoint = `/v1/payment-receipt/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ name: '404' })
        }
      })
  },
}
</script>
