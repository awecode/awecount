<script setup lang="ts">
import type { Ref } from 'vue'
import Decimal from 'decimal.js'
import DateConverter from 'src/components/date/VikramSamvat.js'
import useApi from 'src/composables/useApi'
import checkPermissions from 'src/composables/checkPermissions'
import { useLoginStore } from 'src/stores/login-info'

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
  landed_cost_rows: Array<{ type: string, amount: number, is_percentage: boolean, currency: string, description: string }>
}

const metaData = {
  title: 'Purchase/Expenses | Awecount',
}
const route = useRoute()
const router = useRouter()
useMeta(metaData)
const store = useLoginStore()
const $q = useQuasar()
const fields: Ref<Fields | null> = ref(null)
const modeOptions: Ref<Array<object> | null> = ref(null)
const isDeleteOpen: Ref<boolean> = ref(false)
const deleteMsg: Ref<string> = ref('')
const isLoading: Ref<boolean> = ref(false)
const errors = ref({})
const submitChangeStatus = (id: number, status: string) => {
  isLoading.value = true
  let endpoint = ''
  let body: null | object = null
  if (status === 'Paid') {
    endpoint = `/api/company/${route.params.company}/purchase-vouchers/${id}/mark_as_paid/`
    body = { method: 'POST' }
  } else if (status === 'Cancelled') {
    endpoint = `/api/company/${route.params.company}/purchase-vouchers/${id}/cancel/`
    body = { method: 'POST', body: { message: deleteMsg.value } }
  }
  useApi(endpoint, body)
    .then(() => {
      onStatusChange(status)
      isLoading.value = false
    })
    .catch((data) => {
      if (data.status === 422) {
        useHandleCancelInconsistencyError(endpoint, data, body.body, $q)
          .then(() => {
            isLoading.value = false
            onStatusChange(status)
          })
          .catch((error) => {
            if (error.status !== 'cancel') {
              $q.notify({
                color: 'negative',
                message: 'Something went Wrong!',
                icon: 'report_problem',
              })
            }
            isLoading.value = false
          })
      } else {
        const parsedError = useHandleFormError(data)
        errors.value = parsedError.errors
        $q.notify({
          color: 'negative',
          message: parsedError.message,
          icon: 'report_problem',
        })
        isLoading.value = false
      }
    })
}
const getDate = computed(() => {
  return DateConverter.getRepresentation(fields.value?.date, store.isCalendarInAD ? 'ad' : 'bs')
})
const discountComputed = computed(() => {
  if (fields?.value.discount_obj) {
    return `${fields.value.discount_obj.value}` + ' ' + `${fields.value.discount_obj.type === 'Amount' ? '-/' : '%'}`
  } else if (fields?.value.discount) {
    return `${fields.value.discount}` + ' ' + `${fields.value.discount_type === 'Amount' ? '-/' : '%'}`
  } else {
    return false
  }
})
const onStatusChange = (status: string) => {
  if (fields.value) {
    fields.value.status = status
    if (status === 'Cancelled') {
      $q.notify({
        color: 'green-6',
        icon: 'check_circle',
        message: 'Voucher has been cancelled.',
      })
      // fields.value.remarks = ('\nReason for cancellation: ' + body?.body.message)
      isDeleteOpen.value = false
    } else if (status === 'Paid') {
      $q.notify({
        color: 'green-6',
        icon: 'check_circle',
        message: 'Voucher Marked as paid.',
      })
    }
  }
}

const averageRate = computed(() => {
  if (!fields.value.rows || !fields.value.landed_cost_rows) return 0
  const totalAmount = fields.value.rows.reduce((sum, row) => sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0'))
  const totalLandedCosts = fields.value.landed_cost_rows.reduce((sum, row) => sum.add(row.amount || '0'), new Decimal('0'))
  const totalQuantity = fields.value.rows.reduce((sum, row) => sum.add(row.quantity || '0'), new Decimal('0'))
  return totalAmount.add(totalLandedCosts).div(totalQuantity).toNumber()
})

const createCopyModalOpen = ref(false)
const createCopy = () => {
  const endpoint = `/api/company/${route.params.company}/purchase-vouchers/${fields.value?.id}/create-a-copy/`
  useApi(endpoint, { method: 'POST' }, false, true)
    .then((res) => {
      createCopyModalOpen.value = false
      router.push({ path: `/${route.params.company}/purchase/vouchers/${res?.id}/edit` })
    })
    .catch((error) => {
      if (error.response && error.response.status === 404) {
        router.replace({ path: '/ErrorNotFound' })
      }
    })
}


const endpoint = `/api/company/${route.params.company}/purchase-vouchers/${route.params.id}/details/`
useApi(endpoint, { method: 'GET' }, false, true)
  .then((data) => {
    fields.value = data
    modeOptions.value = data.available_bank_accounts
  })
  .catch((error) => {
    if (error.response && error.response.status == 404) {
      router.replace({ path: '/ErrorNotFound' })
    }
  })

</script>

<template>
  <div>
    <div v-if="fields" class="sales-invoice">
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white">
          <div class="text-h6">
            <span>Purchase Invoice | {{ fields?.status }} | #{{ fields?.voucher_no }}</span>
          </div>
        </q-card-section>

        <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Party
              </div>
              <div class="col-6">
                {{ fields?.party_name }}
              </div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Status
              </div>
              <div class="col-6">
                {{ fields?.status }}
              </div>
            </div>
          </div>
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Date
              </div>
              <div class="col-6">
                {{ getDate }}
              </div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Payment Mode
              </div>
              <div class="col-6">
                {{ fields?.payment_mode ?? 'Credit' }}
              </div>
            </div>
          </div>
          <div v-if="discountComputed" class="col-12 col-md-6 q-gutter-y-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Discount
              </div>
              <div class="col-6">
                {{ discountComputed }}
              </div>
            </div>
          </div>
          <div v-if="fields.purchase_order_numbers && fields.purchase_order_numbers.length > 0" class="col-12 col-md-6 q-gutter-y-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Purchase Order(s)
              </div>
              <div class="col-6">
                {{ fields.purchase_order_numbers.join(',') }}
              </div>
            </div>
          </div>
        </q-card>
      </q-card>
      <q-card id="to_print" class="q-mx-lg">
        <q-card-section>
          <ViewerTable :fields="fields" />
        </q-card-section>
      </q-card>

      <q-card v-if="fields?.landed_cost_rows?.length" class="q-mx-lg q-my-md">
        <q-card-section>
          <div class="text-subtitle2 text-grey-9 q-mb-md">
            Landed Costs:
          </div>
          <q-table
            bordered
            flat
            hide-pagination
            :columns="[
              { name: 'type', label: 'Cost Type', field: 'type', align: 'left', style: 'width: 20%' },
              { name: 'amount', label: 'Amount', field: 'amount', align: 'right', style: 'width: 25%' },
              { name: 'description', label: 'Description', field: 'description', align: 'left', style: 'width: 50%' },
            ]"
            :rows="fields.landed_cost_rows"
          >
            <template #body-cell-amount="props">
              <q-td :props="props">
                <FormattedNumber
                  type="currency"
                  :value="props.row.amount"
                />
              </q-td>
            </template>
            <template #bottom-row>
              <q-tr>
                <q-td colspan="3">
                  Average rate per item:

                  <FormattedNumber
                    class="text-bold"
                    type="currency"
                    :value="averageRate"
                  />
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
      <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9">Remarks:</span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none">
        <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-gutter-y-md q-mb-md">
          <q-btn
            v-if="checkPermissions('purchasevoucher.update')"
            color="orange-5"
            icon="edit"
            label="Edit"
            :to="`/${$route.params.company}/purchase/vouchers/${fields.id}/edit`"
          />
          <q-btn
            v-if="fields?.status === 'Issued' && checkPermissions('purchasevoucher.update')"
            color="green-6"
            icon="mdi-check-all"
            label="mark as paid"
            :loading="isLoading"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
          />
          <q-btn
            v-if="checkPermissions('purchasevoucher.update')"
            color="red-5"
            icon="cancel"
            label="Cancel"
            :loading="isLoading"
            @click.prevent="() => (isDeleteOpen = true)"
          />
        </div>
        <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end">
          <q-btn
            data-testid="create-copy"
            label="Create a copy"
            @click="createCopyModalOpen = true"
          />
          <q-btn
            v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
            color="blue-7"
            icon="books"
            label="Journal Entries"
            :to="`/${$route.params.company}/purchase/vouchers/${fields.id}/journal-entries`"
          />
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
              <q-btn label="Confirm" @click="() => submitChangeStatus(fields?.id, 'Cancelled')" />
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
      <q-dialog v-model="createCopyModalOpen">
        <q-card style="min-width: min(60vw, 800px)">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6 flex justify-between">
              <span class="q-mx-md">Create a copy</span>
              <q-btn
                v-close-popup
                dense
                flat
                round
                class="text-white bg-red-500"
                icon="close"
              />
            </div>
          </q-card-section>
          <q-card-section class="q-mx-md flex flex-col gap-4">
            <!-- message -->
            <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
              Are you sure you want to create a copy of this purchase voucher?
            </div>
            <div class="row justify-end">
              <q-btn
                class="q-mt-md"
                color="orange-5"
                label="Create Copy"
                @click="createCopy"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </div>
</template>

<style scoped>
@media print {
  /* @import url("https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap"); */

  .q-card {
    box-shadow: none;
    padding: 0;
  }
}
</style>
