<script lang="ts">
import type { Ref } from 'vue'

export default {
  setup() {
    const metaData = {
      title: 'Inventory Adjustment | Awecount',
    }
    const route = useRoute()
    const router = useRouter()
    useMeta(metaData)
    const $q = useQuasar()
    const fields: Ref<Record<string, any>> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const errors = ref({})
    const loading = ref(false)

    const onCancelClick = () => {
      const url = `/api/company/${route.params.company}/inventory-adjustment/${fields.value.id}/cancel/`
      const body = {
        message: deleteMsg.value,
      }
      loading.value = true
      useApi(url, {
        method: 'POST',
        body,
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Cancelled',
            icon: 'check_circle',
          })
          fields.value.status = 'Cancelled'
          fields.value.remarks = (`\nReason for cancellation: ${deleteMsg.value}`)
          isDeleteOpen.value = false
          loading.value = false
        })
        .catch((err) => {
          if (err.status === 422) {
            useHandleCancelInconsistencyError(url, err, body, $q)
              .then(() => {
                $q.notify({
                  color: 'positive',
                  message: 'Cancelled',
                  icon: 'check_circle',
                })
                fields.value.status = 'Cancelled'
                fields.value.remarks = (`\nReason for cancellation: ${deleteMsg.value}`)
                isDeleteOpen.value = false
                loading.value = false
              })
              .catch((error) => {
                if (error.status !== 'cancel') {
                  $q.notify({
                    color: 'negative',
                    message: 'Something went Wrong!',
                    icon: 'report_problem',
                  })
                }
                loading.value = false
              })
          } else {
            const parsedError = useHandleFormError(err)
            errors.value = parsedError.errors
            $q.notify({
              color: 'negative',
              message: parsedError.message,
              icon: 'report_problem',
            })
          }
          loading.value = false
        })
    }

    const onPrintclick = (bodyOnly: boolean, noApiCall = false) => {
      // const endpoint = `/api/company/sales-voucher/${fields.value.id}/log-print/`
      // useApi(endpoint, { method: 'POST' })
      //   .then(() => {
      //     if (fields.value) {
      //       fields.value.print_count = fields.value?.print_count + 1
      //     }
      //   })
      //   .catch((err) => console.log('err from the api', err))
      window.print()
    }

    const endpoint = `/api/company/${route.params.company}inventory-adjustment/${route.params.id}/`
    useApi(endpoint, { method: 'GET' }, false, true)
      .then((data) => {
        fields.value = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          router.replace({ path: '/ErrorNotFound' })
        }
      })

    return {
      fields,
      errors,
      checkPermissions,
      formatNumberWithComma,
      loading,
      isDeleteOpen,
      deleteMsg,
      onCancelClick,
      onPrintclick,
    }
  },

}
</script>

<template>
  <div v-if="fields">
    <print-header />
    <div>
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white">
          <div class="text-h6 d-print-none">
            <span>Inventory Adjustment Voucher | {{ fields?.status }}
              <span v-if="fields?.voucher_no">| # {{ fields?.voucher_no }}</span>
            </span>
          </div>
        </q-card-section>
        <div class="q-mx-lg q-pa-lg row text-grey-8 text-body2 grid grid-cols-2 gap-5">
          <div class="grid grid-cols-2">
            <div class="">
              Date
            </div>
            <div class="">
              {{ fields.date }}
            </div>
          </div>
          <div class="grid grid-cols-2">
            <div class="">
              Status
            </div>
            <div class="">
              {{ fields.status }}
            </div>
          </div>
          <div class="grid grid-cols-2">
            <div class="">
              Purpose
            </div>
            <div class="">
              {{ fields.purpose }}
            </div>
          </div>
        </div>
      </q-card>
      <q-card id="to_print" class="q-mx-lg">
        <q-card-section>
          <q-markup-table flat bordered>
            <thead>
              <q-tr class="text-left">
                <q-th data-testid="SN">
                  SN
                </q-th>
                <q-th data-testid="Particular">
                  Particular
                </q-th>
                <q-th data-testid="Qty">
                  Qty
                </q-th>
                <q-th data-testid="Rate">
                  Rate
                </q-th>
                <q-th data-testid="Amount" class="text-right">
                  Amount
                </q-th>
              </q-tr>
            </thead>
            <tbody class="text-left">
              <q-tr v-for="(row, index) in fields?.rows" :key="index">
                <q-td>
                  {{ index + 1 }}
                </q-td>
                <q-td>
                  {{ row.item_name }} <br />
                  <span v-if="row.description" style="font-size: 11px" class="text-grey-8">
                    <div v-for="(des, index) in row.description.split('\n')" :key="index" class="whitespace-normal">
                      {{ des }}
                    </div>
                  </span>
                </q-td>
                <q-td>
                  <span>{{ row.quantity }}
                    <span class="text-grey-9">
                      ({{ row.unit_name }})</span></span>
                </q-td>
                <q-td>
                  <span>{{ $nf(row.rate) }}</span>
                </q-td>
                <q-td class="text-right">
                  <span>{{ $nf(row.rate * row.quantity) }}</span>
                </q-td>
              </q-tr>
              <q-tr class="text-subtitle2">
                <q-td />
                <q-td /><q-td /><q-td> Total </q-td><q-td class="text-right">
                  {{
                    formatNumberWithComma(fields?.total_amount)
                  }}
                </q-td>
              </q-tr>
            </tbody>
          </q-markup-table>
        </q-card-section>
      </q-card>
      <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9"> Remarks: </span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none">
        <div>
          <div class="row q-gutter-x-md q-gutter-y-md q-mb-md">
            <q-btn
              v-if="checkPermissions('InventoryAdjustmentVoucherModify') && (fields?.status !== 'Cancelled')"
              color="orange-5"
              label="Edit"
              icon="edit"
              :to="`/${$route.params.company}/items/inventory-adjustment/${fields?.id}/`"
            />
            <q-btn
              v-if="checkPermissions('SalesCancel') && fields?.status !== 'Cancelled'"
              color="red-5"
              label="Cancel"
              icon="cancel"
              :loading="loading"
              @click.prevent="() => (isDeleteOpen = true)"
            />
          </div>
        </div>
        <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end">
          <q-btn
            :label="`Print ${fields?.print_count ? `Copy ${['Draft', 'Cancelled'].includes(fields?.status)
              ? ''
              : `# ${(fields?.print_count || 0)}`
            }` : ''}`
            "
            icon="print"
            @click="() => onPrintclick(false, fields?.status === 'Draft')"
          />
          <q-btn
            v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
            color="blue-7"
            label="Journal Entries"
            icon="books"
            :to="`/${$route.params.company}/journal-entries/inventory-adjustment/${fields.id}/`"
          />
        </div>
        <q-dialog v-model="isDeleteOpen" class="overflow-visible" @before-hide="errors = {}">
          <q-card style="min-width: min(40vw, 500px)" class="overflow-visible">
            <q-card-section class="bg-red-6 flex justify-between">
              <div class="text-h6 text-white">
                <span>Confirm Cancellation?</span>
              </div>
              <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
            </q-card-section>

            <q-card-section class="q-ma-md">
              <q-input
                v-model="deleteMsg"
                autofocus
                type="textarea"
                outlined
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
    </div>
  </div>
</template>

<style scoped lang="scss">
@media print {
  @import url('https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap');

  .d-print-none {
    display: none;
    visibility: hidden;
    width: none;
  }
}
</style>
