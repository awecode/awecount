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
            <q-select class="col-md-6 col-12" v-model="fields.finished_product"
              :options="formDefaults?.collections?.finished_products" option-value="id" option-label="name" map-options
              emit-value label="Finished Product *" :error-message="errors.finished_product"
              :error="!!errors.finished_product" :disable="isEdit"></q-select>
            <q-select class="col-md-6 col-12" v-model="fields.unit_id" :options="formDefaults?.collections?.units"
              option-value="id" option-label="name" map-options emit-value label="Unit *"
              :error-message="errors.unit_id" :error="!!errors.unit_id"></q-select>
            <q-input v-model="fields.quantity" label="Quantity *" class="col-md-6 col-12"
              :error-message="errors.quantity" :error="!!errors.quantity" type="number"></q-input>
            <q-input v-model="fields.rate" label="Rate *" class="col-md-6 col-12" :error-message="errors.rate"
              :error="!!errors.rate" type="number"></q-input>
          </div>
          <div class="q-mt-lg">
            <AdjustmentInvoiceTable label="Raw Material(s)" v-model="fields.rows" :minimal="true"
              :itemOptions="formDefaults?.collections?.items" :unitOptions="formDefaults?.collections?.units"
              :errors="errors?.rows" @deleteRow="(index) => deleteRow(index, errors)">
            </AdjustmentInvoiceTable>
          </div>
          <div class="q-mt-lg">
            <q-input v-model="fields.remarks" label="Remarks" class="col-6" :error-message="errors.remarks"
              :error="!!errors.remarks" type="textarea" autogrow />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn v-if="checkPermissions('BillOfMaterialModify') && isEdit && fields.status !== 'Cancelled'"
            :loading="loading" @click.prevent="onSubmitClick(fields.status)" color="green" label="Update"
            type="submit" />
          <q-btn v-if="!isEdit && checkPermissions('BillOfMaterialCreate')" :loading="loading"
            @click.prevent="onSubmitClick('Issued')" color="green" label="Create" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/bill-of-material/'
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
        } else formData.fields.value.deleted_rows = [deletedObj]
      }
      if (errors && errors.rows && Array.isArray(errors)) {
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

    return {
      ...formData, checkPermissions, deleteRow, onSubmitClick
    }
  },
}
</script>
