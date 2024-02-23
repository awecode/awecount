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
            <q-select class="col-md-6 col-12" v-model="fields.purpose" :options="purposeChoices"
              label="Purpose"></q-select>
          </div>
          <div class="q-mt-md">
            <AdjustmentInvoiceTable></AdjustmentInvoiceTable>
          </div>
          <div class="q-mt-lg">
            <q-input v-model="fields.description" label="Remarks*" class="col-6" :error-message="errors.description"
              :error="!!errors.description" type="textarea" autogrow />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('BrandModify') && isEdit" :loading="loading" @click.prevent="submitForm"
            color="green" label="Update" class="q-ml-auto" type="submit" />
          <q-btn v-if="!isEdit && checkPermissions('BrandCreate')" :loading="loading" @click.prevent="submitForm"
            color="green" label="Create" class="q-ml-auto" type="submit" />
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
    useMeta(metaData)
    return {
      ...formData, checkPermissions, purposeChoices
    }
  },
}
</script>
