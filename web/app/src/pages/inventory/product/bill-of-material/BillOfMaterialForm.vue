<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

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
      successRoute: '/items/bill-of-material/list/',
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
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Bill of Material</span>
          <span v-else>Update Bill of Material | {{ fields.finished_product_name }} </span>
        </div>
      </q-card-section>

      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.finished_product"
              class="col-md-6 col-12"
              :options="formDefaults?.collections?.finished_products"
              option-value="id"
              option-label="name"
              map-options
              emit-value
              label="Finished Product *"
              :error-message="errors.finished_product"
              :error="!!errors.finished_product"
              :disable="isEdit"
            />
            <q-select
              v-model="fields.unit_id"
              class="col-md-6 col-12"
              :options="formDefaults?.collections?.units"
              option-value="id"
              option-label="name"
              map-options
              emit-value
              label="Unit *"
              :error-message="errors.unit_id"
              :error="!!errors.unit_id"
            />
            <q-input
              v-model="fields.quantity"
              label="Quantity *"
              class="col-md-6 col-12"
              :error-message="errors.quantity"
              :error="!!errors.quantity"
              type="number"
            />
            <q-input
              v-model="fields.rate"
              label="Rate *"
              class="col-md-6 col-12"
              :error-message="errors.rate"
              :error="!!errors.rate"
              type="number"
            />
          </div>
          <div class="q-mt-lg">
            <AdjustmentInvoiceTable
              v-model="fields.rows"
              label="Raw Material(s)"
              :minimal="true"
              :item-options="formDefaults?.collections?.items"
              :unit-options="formDefaults?.collections?.units"
              :errors="errors?.rows"
              :finished-product="fields.finished_product"
              @delete-row="(index) => deleteRow(index, errors)"
            />
          </div>
          <div class="q-mt-lg">
            <q-input
              v-model="fields.remarks"
              label="Remarks"
              class="col-6"
              :error-message="errors.remarks"
              :error="!!errors.remarks"
              type="textarea"
              autogrow
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('billofmaterial.modify') && isEdit && fields.status !== 'Cancelled'"
            :loading="loading"
            color="green"
            label="Update"
            type="submit"
            @click.prevent="onSubmitClick(fields.status)"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('billofmaterial.create')"
            :loading="loading"
            color="green"
            label="Create"
            type="submit"
            @click.prevent="onSubmitClick('Issued')"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
