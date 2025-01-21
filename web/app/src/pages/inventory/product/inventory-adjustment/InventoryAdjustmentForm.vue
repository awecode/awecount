<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/inventory-adjustment/`
    const metaData = {
      title: 'Inventory Adjustment | Awecount',
    }
    useMeta(metaData)
    const isAdjustmentImportOpen = ref(false)
    const importErrorData = []
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref(null)
    const purposeChoices = [
      {
        label: 'Stock In',
        value: 'Stock In',
      },
      {
        label: 'Stock Out',
        value: 'Stock Out',
      },
      {
        label: 'Damaged',
        value: 'Damaged',
      },
      {
        label: 'Expired',
        value: 'Expired',
      },
    ]
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/inventory/adjustments`,
    })
    formData.fields.value.date = formData.today
    const deleteRow = (index, errors) => {
      if (formData.fields.value.rows[index].id) {
        const deletedObj = { ...formData.fields.value.rows[index] }
        if (formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows.push(deletedObj)
        } else {
          formData.fields.value.deleted_rows = [deletedObj]
        }
      }
      if (errors?.rows) {
        errors.rows.splice(index, 1)
      }
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try {
        await formData.submitForm()
      } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    const onXlsFileImport = (items) => {
      if (!formData.fields.value.rows) {
        formData.fields.value.rows = []
      }
      formData.fields.value.rows.push(...items.items)
      importErrorData.push(...items.unadjusted_items)
    }
    const onCancelClick = () => {
      const url = `/api/company/${route.params.company}/inventory-adjustment/${formData.fields.value.id}/cancel/`
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
          formData.fields.value.remarks = `\nReason for cancellation: ${deleteMsg.value}`
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
                formData.fields.value.remarks = `\nReason for cancellation: ${deleteMsg.value}`
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
      ...formData,
      checkPermissions,
      purposeChoices,
      deleteRow,
      onSubmitClick,
      isDeleteOpen,
      deleteMsg,
      onCancelClick,
      isAdjustmentImportOpen,
      onXlsFileImport,
      importErrorData,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Inventory Adjustment Voucher</span>
          <span v-else>Update Inventory Adjustment Voucher | {{ fields.status }} | # {{ fields.voucher_no }}</span>
        </div>
      </q-card-section>
      <div class="flex justify-end p-4">
        <q-btn class="flex justify-end text-green" label="Import From XlS" @click="isAdjustmentImportOpen = true" />
      </div>
      <q-dialog v-model="isAdjustmentImportOpen">
        <q-card style="min-width: min(80vw, 900px)">
          <q-btn
            dense
            push
            round
            color="red"
            icon="close"
            style="position: absolute; right: 8px; top: 8px; z-index: 50"
            text-color="white"
            @click="isAdjustmentImportOpen = false"
          />
          <InventoryAdjustmentImport @modal-close="isAdjustmentImportOpen = false" @on-import-success="onXlsFileImport" />
        </q-card>
      </q-dialog>
      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Date*"
              :error="!!errors?.date"
              :error-message="errors?.date"
            />
            <q-select
              v-model="fields.purpose"
              emit-value
              map-options
              class="col-md-6 col-12"
              label="Purpose"
              option-label="label"
              option-value="value"
              :disable="isEdit"
              :error="!!errors.purpose"
              :error-message="errors.purpose"
              :options="purposeChoices"
            />
          </div>
          <div class="q-mt-lg">
            <AdjustmentInvoiceTable
              v-model="fields.rows"
              :errors="errors?.rows"
              :item-options="formDefaults?.collections?.items"
              :unit-options="formDefaults?.collections?.units"
              @delete-row="(index) => deleteRow(index, errors)"
            />
          </div>
          <div class="q-mt-lg">
            <q-input
              v-model="fields.remarks"
              autogrow
              class="col-6"
              label="Remarks*"
              type="textarea"
              :error="!!errors.remarks"
              :error-message="errors.remarks"
            />
          </div>
        </q-card-section>
        <div v-if="importErrorData.length">
          <div class="text-sm text-gray">
            Following item codes failed to import:
          </div>
          <div class="grid grid-cols-12">
            <div v-for="item in importErrorData" :key="item">
              <div>{{ item }}</div>
            </div>
          </div>
        </div>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('inventoryadjustmentvoucher.delete') && isEdit && fields.status !== 'Cancelled'"
            color="red"
            label="Cancel"
            :loading="loading"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="checkPermissions('inventoryadjustmentvoucher.modify') && isEdit && fields.status !== 'Cancelled'"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick(fields.status)"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('inventoryadjustmentvoucher.create')"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick('Issued')"
          />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen" @before-hide="delete errors.message">
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
    </q-card>
  </q-form>
</template>
