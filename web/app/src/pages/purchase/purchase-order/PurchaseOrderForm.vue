<script>
import ChallanTable from 'src/components/challan/ChallanTable.vue'
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'

const route = useRoute()
export default {
  setup() {
    const endpoint = `/api/company/${route.params.company}/purchase-order/`
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref('')
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/purchase-order/list/',
    })
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value ? 'Purchase Order Update' : 'Purchase Order Add'
          } | Awecount`,
      }
    })
    const deleteRow = (index, errors, deleteObj) => {
      if (deleteObj) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (errors && Array.isArray(errors.rows)) {
        errors.rows.splice(index, 1)
      }
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.party = ''
    const onCancelClick = () => {
      formData.loading.value = true
      useApi(`/api/company/${route.params.company}/purchase-order/${formData.fields.value.id}/cancel/`, {
        method: 'POST',
        body: {
          message: deleteMsg.value,
        },
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Cancelled',
            icon: 'check_circle',
          })
          formData.fields.value.status = 'Cancelled'
          formData.fields.value.remarks = (`\nReason for cancellation: ${deleteMsg.value}`)
          isDeleteOpen.value = false
          formData.loading.value = false
        })
        .catch((err) => {
          // let message = 'error'
          // if (err.data?.message) {
          //     message = err.data?.message
          // }
          // $q.notify({
          //     color: 'negative',
          //     message,
          //     icon: 'report_problem',
          // })
          const parsedError = useHandleFormError(err)
          formData.errors.value = parsedError.errors
          $q.notify({
            color: 'negative',
            message: parsedError.message,
            icon: 'report_problem',
          })
          formData.loading.value = false
        })
    }
    watch(
      () => formData.fields.value.party,
      (newValue) => {
        if (newValue) {
          const index
            = formData.formDefaults.value.collections?.parties.results.findIndex(
              option => option.id === newValue,
            )
          if (index > -1) {
            formData.fields.value.address
              = formData.formDefaults.value.collections.parties.results[index].address
          }
        }
      },
    )
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      deleteRow,
      onSubmitClick,
      ChallanTable,
      checkPermissions,
      onCancelClick,
      isDeleteOpen,
      deleteMsg,
    }
  },
  // onmounted: () => console.log('mounted'),
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Purchase Order</span>
          <span v-else>Update Purchase Order <span v-if="isEdit && fields?.voucher_no">| {{ fields?.status }} | #
            {{ fields?.voucher_no }}</span></span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.party"
                :options="formDefaults.collections?.parties"
                label="Party *"
                :endpoint="`/api/company/${route.params.company}/purchase-order/create-defaults/parties`"
                :static-option="fields.selected_party_obj"
                :error="errors?.party ? errors?.party : null"
                :modal-component="checkPermissions('PartyCreate') ? PartyForm : null"
              />
              <div></div>
            </div>
            <DatePicker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Date *"
              :error="!!errors?.date"
              :error-message="errors?.date"
            />
          </div>
        </q-card-section>
      </q-card>
      <ChallanTable
        v-if="formDefaults.collections"
        v-model="fields.rows"
        :item-options="formDefaults.collections ? formDefaults.collections.items : null
        "
        used-in="purchase-order"
        :unit-options="formDefaults.collections ? formDefaults.collections.units : null
        "
        :errors="!!errors.rows ? errors.rows : null"
        :is-edit="isEdit"
        @delete-row="(index, deleteObj) => deleteRow(index, errors, deleteObj)"
      />
      <div class="q-px-md">
        <q-input
          v-model="fields.remarks"
          label="Remarks"
          type="textarea"
          autogrow
          class="col-12 col-md-10"
          :error="!!errors?.remarks"
          :error-message="errors?.remarks"
        />
      </div>
      <div class="q-ma-md row q-pb-lg flex justify-end q-gutter-md">
        <q-btn
          v-if="checkPermissions('ChallanCreate') && isEdit && fields.status === 'Issued'"
          :to="`/purchase-voucher/add/?purchase_order=${fields.voucher_no}&fiscal_year=${fields.fiscal_year}`"
          color="blue"
          label="Issue Purchase Voucher"
          :loading="loading"
        />
        <q-btn
          v-if="checkPermissions('PurchaseOrderCancel') && isEdit && fields.status === 'Issued'"
          :loading="loading"
          color="red"
          label="Cancel"
          icon="cancel"
          @click.prevent="isDeleteOpen = true"
        />
        <q-btn
          v-if="checkPermissions('PurchaseOrderModify') && isEdit && fields.status === 'Issued'"
          :loading="loading"
          color="green"
          label="Update"
          @click.prevent="onSubmitClick('Issued')"
        />
        <q-btn
          v-if="checkPermissions('PurchaseOrderCreate') && !isEdit"
          :loading="loading"
          color="green"
          label="Issue"
          @click.prevent="onSubmitClick('Issued')"
        />
      </div>
    </q-card>
    <q-dialog v-model="isDeleteOpen" @before-hide="delete errors?.message">
      <q-card style="min-width: min(40vw, 500px)">
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
  </q-form>
</template>
