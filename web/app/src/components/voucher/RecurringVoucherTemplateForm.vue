<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { parseErrors } from 'src/utils/helpers'
import { capitalize } from 'vue'
import PurchaseVoucherFormFields from './PurchaseVoucherFormFields.vue'
import SalesVoucherFormFields from './SalesVoucherFormFields.vue'

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
  createDefaultsEndpoint: `${endpoint}create-defaults/?type=${capitalizedType} Voucher`,
})

const { fields, formDefaults, errors, isEdit, loading, submitForm, today } = formData

useMeta({
  title: `Recurring ${capitalizedType} Invoice ${isEdit.value ? 'Update' : 'Add'} | Awecount`,
})

const invoiceDataErrors = ref({})

watch(
  () => errors.value,
  () => {
    if (errors.value.invoice_data) {
      invoiceDataErrors.value = parseErrors(errors.value.invoice_data)
    }
  },
)

useMeta(() => ({
  title: `${isEdit.value ? `Recurring ${capitalizedType} Invoice Template Update` : `Recurring ${capitalizedType} Invoice Add`} | Awecount`,
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

const timeUnits = ['Day(s)', 'Week(s)', 'Month(s)', 'Year(s)']
</script>

<template>
  <q-form v-if="Object.keys(fields).length" autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Recurring {{ capitalizedType }} Invoice Template</span>
          <span v-else>Update Recurring {{ capitalizedType }} Invoice Template</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-h6">
          {{ capitalizedType }} Voucher Details
        </div>
      </q-card-section>
      <component
        :is="type === 'sales' ? SalesVoucherFormFields : PurchaseVoucherFormFields"
        v-model:errors="invoiceDataErrors"
        v-model:fields="fields.invoice_data"
        :form-defaults="formDefaults"
        :is-edit="isEdit"
        :is-template="true"
        :today="today"
      />

      <q-card-section>
        <div class="text-h6">
          Recurring Template Details
        </div>
      </q-card-section>
      <q-card-section>
        <div class="row q-col-gutter-md">
          <q-input
            v-model="fields.title"
            class="col-12"
            label="Title"
            :error="!!errors.title"
            :error-message="errors.title"
          />
        </div>
        <div class="row q-col-gutter-md">
          <q-input
            v-model.number="fields.repeat_interval"
            class="col-6 col-md-3"
            label="Repeat Interval"
            type="number"
            :error="!!errors.repeat_interval"
            :error-message="errors.repeat_interval"
          />
          <q-select
            v-model="fields.repeat_interval_time_unit"
            class="col-6 col-md-3"
            label=""
            :error="!!errors.repeat_interval_time_unit"
            :error-message="errors.repeat_interval_time_unit"
            :options="timeUnits"
          />
          <q-input
            v-model.number="fields.due_date_after"
            class="col-4 col-md-2"
            label="Due Date"
            type="number"
            :error="!!errors.due_date_after"
            :error-message="errors.due_date_after"
          />
          <q-select
            v-model="fields.due_date_after_time_unit"
            class="col-4 col-md-2"
            label=""
            :error="!!errors.due_date_after_time_unit"
            :error-message="errors.due_date_after_time_unit"
            :options="timeUnits"
          />
          <div class="col-4 col-md-2 q-mt-md flex items-center">
            after invoice date
          </div>
        </div>
        <div class="row q-col-gutter-md">
          <q-input
            v-model="fields.start_date"
            class="col-12 col-md-4"
            label="Start Date"
            type="date"
            :error="!!errors.start_date"
            :error-message="errors.start_date"
          />
          <q-input
            v-model="fields.end_date"
            class="col-12 col-md-4"
            label="End Date"
            type="date"
            :error="!!errors.end_date"
            :error-message="errors.end_date"
          />
          <q-input
            v-model.number="fields.end_after"
            class="col-12 col-md-4"
            hint="Invoice creation will stop after creating this number of invoices"
            label="End After"
            type="number"
            :error="!!errors.end_after"
            :error-message="errors.end_after"
          />
        </div>
        <div class="row q-col-gutter-md">
          <q-checkbox v-model="fields.is_active" class="col-12 col-md-6" label="Is Active" />
          <q-checkbox v-model="fields.send_email" class="col-12 col-md-6" label="Send Email" />
        </div>
      </q-card-section>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          v-if="!isEdit && checkPermissions('RecurringVoucherTemplateCreate')"
          color="blue"
          data-testid="issue-btn"
          label="Save"
          type="submit"
          :loading="loading"
          @click.prevent="submitForm()"
        />
        <q-btn
          v-if="isEdit && checkPermissions('RecurringVoucherTemplateModify')"
          color="orange-8"
          data-testid="update-btn"
          label="Update"
          type="submit"
          :loading="loading"
          @click.prevent="submitForm()"
        />
      </div>
    </q-card>
  </q-form>
</template>
