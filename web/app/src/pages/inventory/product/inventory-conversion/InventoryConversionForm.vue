<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/inventory-conversion/`
    const metaData = {
      title: 'Inventory Conversion | Awecount',
    }
    useMeta(metaData)
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref(null)
    const finishedProductData = ref([])
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/items/inventory-conversion/list/',
    })
    formData.fields.value.date = formData.today
    const deleteRow = (index, errors) => {
      if (formData.fields.value.rows && formData.fields.value.rows[index].id) {
        const deletedObj = { ...formData.fields.value.rows[index] }
        if (formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows.push(deletedObj)
        } else {
          formData.fields.value.deleted_rows = [deletedObj]
        }
      }
      if (errors && errors.rows && Array.isArray(errors)) {
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
    const onCancelClick = () => {
      const url = `/api/company/${route.params.company}/inventory-conversion/${formData.fields.value.id}/cancel/`
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

    const handleFinishedProductUpdate = (data) => {
      const rows = data.rows.map((item) => {
        return {
          item_id: item.item_id,
          quantity: item.quantity,
          unit_id: item.unit_id,
          transaction_type: 'Cr',
        }
      })
      rows.push({
        item_id: data.finished_product,
        quantity: data.quantity,
        unit_id: data.unit_id,
        rate: data.rate,
        transaction_type: 'Dr',
      })
      formData.fields.value.rows = rows
      formData.fields.value.remarks = data.remarks
    }
    const onFinishedProductClick = (id) => {
      const index = finishedProductData.value.findIndex((item) => item.id === id)
      if (index > -1) {
        handleFinishedProductUpdate(finishedProductData.value[index])
      } else {
        useApi(`/api/company/${route.params.company}/bill-of-material/${id}/`, {
          method: 'GET',
        }).then((data) => {
          finishedProductData.value.push(data)
          handleFinishedProductUpdate(data)
        })
      }
    }
    return {
      ...formData,
      checkPermissions,
      deleteRow,
      onSubmitClick,
      isDeleteOpen,
      deleteMsg,
      onCancelClick,
      onFinishedProductClick,
    }
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Inventory Conversion Voucher</span>
          <span v-else>Update Inventory Conversion Voucher | {{ fields.status }} | # {{ fields.voucher_no }}</span>
        </div>
      </q-card-section>

      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-select v-model="fields.finished_product" class="col-md-6 col-12" :options="formDefaults?.collections?.finished_products" option-value="id" option-label="name" map-options emit-value label="Finished Product" :disable="isEdit" @update:model-value="onFinishedProductClick" />
            <date-picker v-model="fields.date" label="Date*" class="col-md-6 col-12" :error="!!errors?.date" :error-message="errors?.date" />
          </div>
          <div class="q-mt-lg grid 2xl:grid-cols-12 2xl:gap-x-8 grid-cols-1 gap-y-8">
            <div class="col-span-4">
              <div class="mb-2 pl-2">Raw Material(s)</div>
              <InventoryConversionTable v-model="fields.rows" :item-options="formDefaults?.collections?.items" :unit-options="formDefaults?.collections?.units" :errors="errors?.rows" type="Cr" @delete-row="(index) => deleteRow(index, errors)" />
            </div>
            <div class="col-span-8">
              <div class="mb-2 pl-2">Finished Product(s)</div>
              <InventoryConversionTable v-model="fields.rows" :item-options="formDefaults?.collections?.items" :unit-options="formDefaults?.collections?.units" :errors="errors?.rows" type="Dr" @delete-row="(index) => deleteRow(index, errors)" />
            </div>
          </div>
          <div class="q-mt-lg">
            <q-input v-model="fields.remarks" label="Remarks*" class="col-6" :error-message="errors.remarks" :error="!!errors.remarks" type="textarea" autogrow />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn v-if="checkPermissions('inventoryconversionvoucher.delete') && isEdit && fields.status !== 'Cancelled'" :loading="loading" color="red" label="Cancel" @click.prevent="isDeleteOpen = true" />
          <q-btn v-if="checkPermissions('inventoryconversionvoucher.modify') && isEdit && fields.status !== 'Cancelled'" :loading="loading" color="green" label="Update" type="submit" @click.prevent="onSubmitClick(fields.status)" />
          <q-btn v-if="!isEdit && checkPermissions('inventoryconversionvoucher.create')" :loading="loading" color="green" label="Create" type="submit" @click.prevent="onSubmitClick('Issued')" />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen" @before-hide="delete errors.message">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6 flex justify-between">
            <div class="text-h6 text-white">
              <span>Confirm Cancellation?</span>
            </div>
            <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
          </q-card-section>

          <q-card-section class="q-ma-md">
            <q-input v-model="deleteMsg" autofocus type="textarea" outlined :error="!!errors?.message" :error-message="errors?.message" />
            <div class="text-right q-mt-lg">
              <q-btn label="Confirm" @click="onCancelClick" />
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-card>
  </q-form>
</template>
