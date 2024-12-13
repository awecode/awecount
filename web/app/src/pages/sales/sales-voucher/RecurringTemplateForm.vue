<template>
  <q-form class="q-pa-lg" autofocus v-if="Object.keys(fields).length">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Recurring Sales Invoice Template</span>
          <span v-else>Update Recurring Sales Invoice Template</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-h6">Sales Voucher Details</div>
      </q-card-section>
      <SalesForm :is-template="true" :formDefaults="formDefaults" v-model:fields="fields.invoice_data"
        v-model:customerMode="customerMode" v-model:aliases="aliases" :isEdit="isEdit"
        v-model:errors="invoiceDataErrors" />

      <q-card-section>
        <div class="text-h6">Recurring Template Details</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-col-gutter-md">
          <q-input class="col-12" v-model="fields.title" label="Title" :error="!!errors.title"
            :error-message="errors.title" />
        </div>
        <div class="row q-col-gutter-md">
          <q-input class="col-12 col-md-6" v-model.number="fields.repeat_interval" label="Repeat Interval"
            :error="!!errors.repeat_interval" :error-message="errors.repeat_interval" type="number" />
          <q-select class="col-12 col-md-6" v-model="fields.repeat_interval_time_unit" label="Repeat Interval Time Unit"
            :options="timeUnits" :error="!!errors.repeat_interval_time_unit"
            :error-message="errors.repeat_interval_time_unit" />
        </div>
        <div class="row q-col-gutter-md">
          <q-input class="col-12 col-md-6" v-model.number="fields.due_date_after" label="Due Date After"
            :error="!!errors.due_date_after" :error-message="errors.due_date_after" type="number" />
          <q-select class="col-12 col-md-6" v-model="fields.due_date_after_time_unit" label="Due Date After Time Unit"
            :options="timeUnits" :error="!!errors.due_date_after_time_unit"
            :error-message="errors.due_date_after_time_unit" />
        </div>
        <div class="row q-col-gutter-md">
          <q-input class="col-12 col-md-4" v-model="fields.start_date" label="Start Date" :error="!!errors.start_date"
            :error-message="errors.start_date" type="date" />
          <q-input class="col-12 col-md-4" v-model="fields.end_date" label="End Date" :error="!!errors.end_date"
            :error-message="errors.end_date" type="date" />
          <q-input class="col-12 col-md-4" v-model.number="fields.end_after" label="End After"
            :error="!!errors.end_after" :error-message="errors.end_after" type="number" />
        </div>
        <div class="row q-col-gutter-md">
          <q-checkbox class="col-12 col-md-6" v-model="fields.is_active" label="Is Active" />
          <q-checkbox class="col-12 col-md-6" v-model="fields.send_email" label="Send Email" />
        </div>
      </q-card-section>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit && checkPermissions('RecurringVoucherTemplateCreate')" :loading="loading"
          @click.prevent="onSubmitClick()" color="blue" label="Save" type="submit" data-testid="issue-btn" />
        <q-btn v-if="isEdit && checkPermissions('RecurringVoucherTemplateModify')" @click.prevent="onSubmitClick()"
          :loading="loading" color="orange-8" label="Update" type="submit" data-testid="update-btn" />
      </div>


    </q-card>
  </q-form>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { parseErrors } from 'src/utils/helpers';

const endpoint = '/v1/recurring-voucher-template/'

const formData = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/sales-voucher/recurring-template/list/',
  createDefaultsEndpoint: 'create-defaults/?type=Sales Voucher',
})

const { fields, formDefaults, errors, isEdit, loading, submitForm, today } =
  formData

const invoiceDataErrors = ref({})

watch(
  () => errors.value,
  () => {
    if (errors.value.invoice_data) {
      invoiceDataErrors.value = parseErrors(errors.value.invoice_data)
    }
  }
)

useMeta(() => ({
  title:
    (isEdit.value ? 'Recurring Sales Invoice Template Update' : 'Recurring Purchase Invoice Add') +
    ' | Awecount',
}))

const customerMode = ref(false)

const onSubmitClick = async () => {
  fields.value.invoice_data.date = today
  fields.value.invoice_data.due_date = today
  if (!customerMode.value) {
    if (aliases.value.length === 0) {
      fields.value.invoice_data.customer_name = null
    }
  } else {
    fields.value.invoice_data.party = null
  }
  await submitForm()
}

if (!isEdit.value) {
  fields.value = {
    invoice_data: {
      due_date: today,
      date: today,
      is_export: false,
    },
    send_email: false,
    is_active: true,
    repeat_interval: 1,
    repeat_interval_time_unit: 'Month(s)',
    due_date_after: 0,
    due_date_after_time_unit: 'Day(s)',
    start_date: today,
    type: 'Sales Voucher',
  }
}

const aliases = ref([])

const timeUnits = [
  'Day(s)', 'Week(s)', 'Month(s)', 'Year(s)'
]

watch(
  () => formDefaults.value,
  () => {
    if (
      formDefaults.value.fields?.invoice_data?.hasOwnProperty('trade_discount')
    ) {
      fields.value.trade_discount = formDefaults.value.fields?.trade_discount
    }
    if (isEdit.value) {
      if (fields.value.invoice_data.customer_name) customerMode.value = true
    } else {
      if (formDefaults.value.fields?.payment_mode) {
        fields.value.invoice_data.payment_mode =
          formDefaults.value.fields.invoice_data.payment_mode
      }
    }
  }
)
</script>
