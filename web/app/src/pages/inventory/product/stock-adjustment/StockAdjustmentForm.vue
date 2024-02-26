<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Stock Adjustment Voucher</span>
          <span v-else>Update Stock Adjustment Voucher</span>
        </div>
      </q-card-section>

      <q-card class="q-ma-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <date-picker label="Date*" v-model="fields.date" class="col-md-6 col-12" :error="!!errors?.date"
              :error-message="errors?.date"></date-picker>
            <q-select class="col-md-6 col-12" v-model="fields.purpose" :options="purposeChoices" option-value="value"
              option-label="label" map-options emit-value label="Purpose" :error-message="errors.purpose"
              :error="!!errors.purpose"></q-select>
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
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('BrandModify') && isEdit" :loading="loading"
            @click.prevent="onSubmitClick(fields.status)" color="green" label="Update" class="q-ml-auto" type="submit" />
          <q-btn v-if="!isEdit && checkPermissions('BrandCreate')" :loading="loading"
            @click.prevent="onSubmitClick('Issued')" color="green" label="Create" class="q-ml-auto" type="submit" />
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
    const endpoint = '/v1/stock-adjustment/'
    const metaData = {
      title: 'Stock Adjustment | Awecount',
    }
    useMeta(metaData)
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
      }
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
    return {
      ...formData, checkPermissions, purposeChoices, deleteRow, onSubmitClick
    }
  },
}
</script>
