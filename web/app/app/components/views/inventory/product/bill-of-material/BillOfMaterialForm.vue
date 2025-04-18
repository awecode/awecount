<script>
import checkPermissions from '@/composables/checkPermissions'
import useForm from '@/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/bill-of-material/`
    const metaData = {
      title: 'Bill of Material | Awecount',
    }
    useMeta(metaData)
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/inventory/bill-of-materials`,
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

    return {
      ...formData,
      checkPermissions,
      deleteRow,
      onSubmitClick,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Bill of Material</span>
          <span v-else>Update Bill of Material | {{ fields.finished_product_name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.finished_product"
              emit-value
              map-options
              class="col-md-6 col-12"
              label="Finished Product *"
              option-label="name"
              option-value="id"
              :disable="isEdit"
              :error="!!errors.finished_product"
              :error-message="errors.finished_product"
              :options="formDefaults?.collections?.finished_products"
            />
            <q-select
              v-model="fields.unit_id"
              emit-value
              map-options
              class="col-md-6 col-12"
              label="Unit *"
              option-label="name"
              option-value="id"
              :error="!!errors.unit_id"
              :error-message="errors.unit_id"
              :options="formDefaults?.collections?.units"
            />
            <q-input
              v-model="fields.quantity"
              class="col-md-6 col-12"
              label="Quantity *"
              type="number"
              :error="!!errors.quantity"
              :error-message="errors.quantity"
            />
            <q-input
              v-model="fields.rate"
              class="col-md-6 col-12"
              label="Rate *"
              type="number"
              :error="!!errors.rate"
              :error-message="errors.rate"
            />
          </div>
          <div class="q-mt-lg">
            <AdjustmentInvoiceTable
              v-model="fields.rows"
              label="Raw Material(s)"
              :errors="errors?.rows"
              :finished-product="fields.finished_product"
              :item-options="formDefaults?.collections?.items"
              :minimal="true"
              :unit-options="formDefaults?.collections?.units"
              @delete-row="(index) => deleteRow(index, errors)"
            />
          </div>
          <div class="q-mt-lg">
            <q-input
              v-model="fields.remarks"
              autogrow
              class="col-6"
              label="Remarks"
              type="textarea"
              :error="!!errors.remarks"
              :error-message="errors.remarks"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('billofmaterial.update') && isEdit && fields.status !== 'Cancelled'"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick(fields.status)"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('billofmaterial.create')"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick('Issued')"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
