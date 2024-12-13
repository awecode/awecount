<template>
  <q-form class="q-pa-lg" autofocus v-if="fields">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>Update Sale Invoice | {{ fields.status }}
            <span v-if="fields.voucher_no">| # {{ fields.voucher_no }}</span></span>
        </div>
      </q-card-section>
      <SalesForm :formDefaults="formDefaults" v-model:fields="fields" v-model:customerMode="customerMode"
        v-model:aliases="aliases" :isEdit="isEdit" v-model:errors="errors" />

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit && checkPermissions('SalesCreate')" :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange-8" label="Save Draft"
          type="submit" data-testid="issue-btn" />
        <q-btn v-if="
          isEdit &&
          fields.status === 'Draft' &&
          checkPermissions('SalesModify')
        " @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" :loading="loading" color="orange-8"
          :label="isEdit ? 'Update Draft' : 'Save Draft'" type="submit" data-testid="draft-btn" />
        <q-btn v-if="checkPermissions('SalesCreate')" :loading="loading" @click.prevent="() =>
          onSubmitClick(
            isEdit
              ? fields.status === 'Draft'
                ? 'Issued'
                : fields.status
              : 'Issued'
          )
          " color="green" :label="isEdit
            ? fields?.status === 'Issued'
              ? 'Update'
              : fields?.status === 'Draft'
                ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft`
                : 'update'
            : `Issue # ${formDefaults.options?.voucher_no || 1}`
            " data-testid="create/update-btn" />
      </div>
    </q-card>
  </q-form>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'

const endpoint = '/v1/sales-voucher/'

const formData = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/sales-voucher/list/',
})

const { fields, formDefaults, errors, isEdit, loading, submitForm, today } =
  formData

useMeta(() => ({
  title:
    (isEdit.value ? 'Sales Invoice Update' : 'Sales Invoice Add') +
    ' | Awecount',
}))

const customerMode = ref(false)

const onSubmitClick = async (status) => {
  const originalStatus = fields.value.status
  fields.value.status = status
  if (!customerMode.value) {
    if (aliases.value.length === 0) {
      fields.value.customer_name = null
    }
  } else {
    fields.value.party = null
  }
  const data = await submitForm()
  if (data && data.hasOwnProperty('error')) {
    fields.value.status = originalStatus
  }
}

if (!isEdit.value) {
  fields.value.due_date = today
  fields.value.date = today
  fields.value.is_export = false
}

const aliases = ref([])

watch(
  () => formDefaults.value,
  () => {
    if (formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
      fields.value.trade_discount = formDefaults.value.fields?.trade_discount
    }
    if (isEdit.value) {
      if (fields.value.customer_name) customerMode.value = true
    } else {
      if (formDefaults.value.fields?.payment_mode) {
        fields.value.payment_mode = formDefaults.value.fields.payment_mode
      }
    }
  }
)
</script>
