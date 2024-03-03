<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Stock Adjustment Voucher</span>
          <span v-else>Update Stock Adjustment Voucher | {{ fields.status }} | # {{ fields.voucher_no }}</span>
        </div>
      </q-card-section>

      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <date-picker label="Date*" v-model="fields.date" class="col-md-6 col-12" :error="!!errors?.date"
              :error-message="errors?.date"></date-picker>
            <q-select class="col-md-6 col-12" v-model="fields.purpose" :options="purposeChoices" option-value="value"
              option-label="label" map-options emit-value label="Purpose" :error-message="errors.purpose"
              :error="!!errors.purpose" :disable="isEdit"></q-select>
          </div>
          <div class="q-mt-lg">
            <AdjustmentInvoiceTable v-model="fields.rows" :itemOptions="formDefaults?.collections?.items"
              :unitOptions="formDefaults?.collections?.units" :errors="errors?.rows"
              @deleteRow="(index) => deleteRow(index, errors)">
            </AdjustmentInvoiceTable>
          </div>
          <div class="q-mt-lg">
            <q-input v-model="fields.remarks" label="Remarks*" class="col-6" :error-message="errors.remarks"
              :error="!!errors.remarks" type="textarea" autogrow />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn v-if="checkPermissions('StockAdjustmentVoucherDelete') && isEdit && fields.status !== 'Cancelled'"
            :loading="loading" @click.prevent="isDeleteOpen = true" color="red" label="Cancel" />
          <q-btn v-if="checkPermissions('StockAdjustmentVoucherModify') && isEdit && fields.status !== 'Cancelled'"
            :loading="loading" @click.prevent="onSubmitClick(fields.status)" color="green" label="Update"
            type="submit" />
          <q-btn v-if="!isEdit && checkPermissions('StockAdjustmentVoucherCreate')" :loading="loading"
            @click.prevent="onSubmitClick('Issued')" color="green" label="Create" type="submit" />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen" @before-hide="delete errors.message">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6 flex justify-between">
            <div class="text-h6 text-white">
              <span>Confirm Cancellation?</span>
            </div>
            <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
          </q-card-section>

          <q-card-section class="q-ma-md">
            <q-input v-model="deleteMsg" autofocus type="textarea" outlined :error="!!errors?.message"
              :error-message="errors?.message"> </q-input>
            <div class="text-right q-mt-lg">
              <q-btn label="Confirm" @click="onCancelClick"></q-btn>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/stock-adjustment/'
    const metaData = {
      title: 'Stock Adjustment | Awecount',
    }
    useMeta(metaData)
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref(null)
    const purposeChoices = [
      {
        label: 'Stock In',
        value: 'Stock In'
      },
      {
        label: 'Stock Out',
        value: 'Stock Out'
      },
      {
        label: 'Damaged',
        value: 'Damaged'
      },
      {
        label: 'Expired',
        value: 'Expired'
      },
    ]
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/items/stock-adjustment/list/',
    })
    formData.fields.value.date = formData.today
    const deleteRow = (index, errors) => {
      if (formData.fields.value.rows[index].id) {
        const deletedObj = { ...formData.fields.value.rows[index] }
        if (formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows.push(deletedObj)
        } else formData.fields.value.deleted_rows = [deletedObj]
      }
      if (!!errors?.rows) {
        errors.rows.splice(index, 1)
      }
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try { await formData.submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    const onCancelClick = () => {
      const url = `/v1/stock-adjustment/${formData.fields.value.id}/cancel/`
      const body = {
        message: deleteMsg.value,
      }
      formData.loading.value = true
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
          formData.fields.value.status = 'Cancelled'
          formData.fields.value.remarks = ('\nReason for cancellation: ' + deleteMsg.value)
          isDeleteOpen.value = false
          formData.loading.value = false
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
                formData.fields.value.status = 'Cancelled'
                formData.fields.value.remarks = ('\nReason for cancellation: ' + deleteMsg.value)
                isDeleteOpen.value = false
                formData.loading.value = false
              })
              .catch((error) => {
                if (error.status !== 'cancel') {
                  $q.notify({
                    color: 'negative',
                    message: 'Something went Wrong!',
                    icon: 'report_problem',
                  })
                }
                formData.loading.value = false
              })
          } else {
            const parsedError = useHandleFormError(err)
            formData.errors.value = parsedError.errors
            $q.notify({
              color: 'negative',
              message: parsedError.message,
              icon: 'report_problem',
            })
          }
          formData.loading.value = false
        })
    }
    return {
      ...formData, checkPermissions, purposeChoices, deleteRow, onSubmitClick, isDeleteOpen, deleteMsg, onCancelClick
    }
  },
}
</script>
