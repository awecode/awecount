<template>
  <div>
    <div v-if="fields" class="sales-invoice">
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white">
          <div class="text-h6">
            <span>Purchase Invoice | {{ fields?.status }} | #{{
              fields?.voucher_no
            }}</span>
          </div>
        </q-card-section>

        <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">Party</div>
              <div class="col-6">{{ fields?.party_name }}</div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">Status</div>
              <div class="col-6">{{ fields?.status }}</div>
            </div>
          </div>
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">Date</div>
              <div class="col-6">{{ getDate }}</div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">Mode</div>
              <div class="col-6">
                {{ fields?.mode }}
              </div>
            </div>
          </div>
          <div v-if="discountComputed" class="col-12 col-md-6 q-gutter-y-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">Discount</div>
              <div class="col-6">{{ discountComputed }}</div>
            </div>
          </div>
          <div v-if="fields.purchase_order_numbers && fields.purchase_order_numbers.length > 0" class="col-12 col-md-6 q-gutter-y-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">Purchase Order(s)</div>
              <div class="col-6">{{ fields.purchase_order_numbers.join(',') }}</div>
            </div>
          </div>
        </q-card>
      </q-card>
      <q-card class="q-mx-lg" id="to_print">
        <q-card-section>
          <ViewerTable :fields="fields" />
        </q-card-section>
      </q-card>
      <q-card class="q-mx-lg q-my-md" v-if="fields?.remarks">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9"> Remarks: </span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none" v-if="fields">
        <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-gutter-y-md q-mb-md">
          <q-btn v-if="checkPermissions('PurchaseVoucherModify')" color="orange-5" label="Edit" icon="edit"
            :to="`/purchase-voucher/${fields?.id}/`" />
          <q-btn v-if="fields?.status === 'Issued' && checkPermissions('PurchaseVoucherModify')"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')" color="green-6" label="mark as paid" :loading="isLoading"
            icon="mdi-check-all" />
          <q-btn v-if="checkPermissions('PurchaseVoucherModify')" color="red-5" label="Cancel" icon="cancel"
            @click.prevent="() => (isDeleteOpen = true)" :loading="isLoading" />
        </div>
        <div v-else class="row q-gutter-x-md q-gutter-y-md q-mb-md">
          <q-btn v-if="checkPermissions('PurchaseVoucherModify')" color="red-5" label="Cancel" icon="cancel"
            @click.prevent="() => (isDeleteOpen = true)" :loading="isLoading"/>
        </div>
        <div>
          <q-btn v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'" color="blue-7"
            label="Journal Entries" icon="books" :to="`/journal-entries/purchase-vouchers/${fields?.id}/`" />
        </div>
      </div>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6">
            <div class="text-h6 text-white">
              <span>Confirm Cancelation?</span>
            </div>
          </q-card-section>

          <q-card-section class="q-ma-md">
            <q-input v-model="deleteMsg" type="textarea" outlined> </q-input>
            <div class="text-right q-mt-lg">
              <q-btn label="Confirm" @click="() => submitChangeStatus(fields?.id, 'Cancelled')"></q-btn>
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
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
import checkPermissions from 'src/composables/checkPermissions'
interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  mode: number
  party_name: string
  date: string
  discount_obj: null | Record<string, string | number>
  discount: null | number
  discount_type: null | 'Amount' | 'Percent'
  purchase_order_numbers: Array<number>
}
export default {
  setup() {
    const metaData = {
      title: 'Purchase/Expenses | Awecount',
    }
    useMeta(metaData)
    const store = useLoginStore()
    const $q = useQuasar()
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const isLoading:Ref<boolean> = ref(false)
    const submitChangeStatus = (id: number, status: string) => {
      isLoading.value = true
      let endpoint = ''
      let body: null | object = null
      if (status === 'Paid') {
        endpoint = `/v1/purchase-vouchers/${id}/mark_as_paid/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/v1/purchase-vouchers/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
      }
      useApi(endpoint, body)
        .then(() => {
          // if (fields.value)
          if (fields.value) {
            fields.value.status = status
            if (status === 'Cancelled') {
              $q.notify({
                color: 'green-6',
                icon: 'check_circle',
                message: 'Voucher has been cancelled.',
              })
              isDeleteOpen.value = false
            } else if (status === 'Paid') {
              $q.notify({
                color: 'green-6',
                icon: 'check_circle',
                message: 'Voucher Marked as paid.',
              })
            }
          }
          isLoading.value = false
        })
        .catch(() => {
          // TODO: Properly Parse Error and show
          $q.notify({
            color: 'red-6',
            message: 'Something Went Wrong!',
            icon: 'report_problem',
          })
          isLoading.value = false
        })
    }
    const getDate = computed(() => {
      return DateConverter.getRepresentation(
        fields.value?.date,
        store.isCalendarInAD ? 'ad' : 'bs'
      )
    })
    const discountComputed = computed(() => {
      if (fields?.value.discount_obj) {
        return (
          `${fields.value.discount_obj.value}` +
          ' ' +
          `${fields.value.discount_obj.type === 'Amount' ? '-/' : '%'}`
        )
      } else if (fields?.value.discount) {
        return (
          `${fields.value.discount}` +
          ' ' +
          `${fields.value.discount_type === 'Amount' ? '-/' : '%'}`
        )
      } else return false
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
      modeOptions,
      discountComputed,
      isDeleteOpen,
      deleteMsg,
      getDate,
      checkPermissions,
      isLoading
    }
  },
  created() {
    const endpoint = `/v1/purchase-vouchers/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' }, false, true)
      .then((data) => {
        this.fields = data
        this.modeOptions = data.available_bank_accounts
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
}
</script>

<style scoped>
@media print {

  /* @import url("https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap"); */

  .q-card {
    box-shadow: none;
    padding: 0;
  }
}
</style>
