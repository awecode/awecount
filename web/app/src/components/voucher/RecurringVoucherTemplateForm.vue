<template>
  <q-form class="q-pa-lg" autofocus v-if="Object.keys(fields).length">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Recurring {{ capitalizedType }} Invoice Template</span>
          <span v-else>Update Recurring {{ capitalizedType }} Invoice Template</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-h6">{{ capitalizedType }} Voucher Details</div>
      </q-card-section>
      <component :is="type === 'sales' ? SalesVoucherFormFields : PurchaseVoucherFormFields" :is-template="true"
        :formDefaults="formDefaults" v-model:fields="fields.invoice_data" :isEdit="isEdit"
        v-model:errors="invoiceDataErrors" :today="today" />

      <q-card-section>
        <div class="text-h6">Recurring Template Details</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-col-gutter-md">
          <q-input class="col-12" v-model="fields.title" label="Title" :error="!!errors.title"
            :error-message="errors.title" />
        </div>
        <div class="row q-col-gutter-md">
          <q-input class="col-6 col-md-3" v-model.number="fields.repeat_interval" label="Repeat Interval"
            :error="!!errors.repeat_interval" :error-message="errors.repeat_interval" type="number" />
          <q-select class="col-6 col-md-3" v-model="fields.repeat_interval_time_unit" label="" :options="timeUnits"
            :error="!!errors.repeat_interval_time_unit" :error-message="errors.repeat_interval_time_unit" />
          <q-input class="col-4 col-md-2" v-model.number="fields.due_date_after" label="Due Date"
            :error="!!errors.due_date_after" :error-message="errors.due_date_after" type="number" />
          <q-select class="col-4 col-md-2" v-model="fields.due_date_after_time_unit" label="" :options="timeUnits"
            :error="!!errors.due_date_after_time_unit" :error-message="errors.due_date_after_time_unit" />
          <div class="col-4 col-md-2 q-mt-md flex items-center">after invoice date</div>
        </div>
        <div class="row q-col-gutter-md">
          <q-input class="col-12 col-md-4" v-model="fields.start_date" label="Start Date" :error="!!errors.start_date"
            :error-message="errors.start_date" type="date" />
          <q-input class="col-12 col-md-4" v-model="fields.end_date" label="End Date" :error="!!errors.end_date"
            :error-message="errors.end_date" type="date" />
          <q-input class="col-12 col-md-4" v-model.number="fields.end_after" label="End After"
            :error="!!errors.end_after" :error-message="errors.end_after" type="number"
            hint="Invoice creation will stop after creating this number of invoices" />
        </div>
        <div class="row q-col-gutter-md">
          <q-checkbox class="col-12 col-md-6" v-model="fields.is_active" label="Is Active" />
          <q-checkbox class="col-12 col-md-6" v-model="fields.send_email" label="Send Email" />
        </div>
      </q-card-section>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit && checkPermissions('RecurringVoucherTemplateCreate')" :loading="loading"
          @click.prevent="submitForm()" color="blue" label="Save" type="submit" data-testid="issue-btn" />
        <q-btn v-if="isEdit && checkPermissions('RecurringVoucherTemplateModify')" @click.prevent="submitForm()"
          :loading="loading" color="orange-8" label="Update" type="submit" data-testid="update-btn" />
      </div>
    </q-card>
  </q-form>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import SalesVoucherFormFields from './SalesVoucherFormFields.vue';
import PurchaseVoucherFormFields from './PurchaseVoucherFormFields.vue';
import { parseErrors } from 'src/utils/helpers';
import { capitalize } from 'vue';

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
})

const capitalizedType = capitalize(props.type)

const endpoint = '/v1/recurring-voucher-template/'

const formData = useForm(endpoint, {
  getDefaults: true,
  queryParams: { type: `${capitalizedType} Voucher` },
  successRoute: `/${props.type}-voucher/recurring-template/list/`,
  createDefaultsEndpoint: `create-defaults/?type=${capitalizedType} Voucher`,
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
    (isEdit.value ? `Recurring ${capitalizedType} Invoice Template Update` : `Recurring ${capitalizedType} Invoice Add`) +
    ' | Awecount',
}))

if (!isEdit.value) {
  fields.value = {
    invoice_data: {},
    send_email: false,
    is_active: true,
    repeat_interval: 1,
    repeat_interval_time_unit: 'Month(s)',
    due_date_after: 0,
    due_date_after_time_unit: 'Day(s)',
    start_date: today,
    type: `${capitalizedType} Voucher`,
  }
}

const timeUnits = [
  'Day(s)', 'Week(s)', 'Month(s)', 'Year(s)'
]
</script>
