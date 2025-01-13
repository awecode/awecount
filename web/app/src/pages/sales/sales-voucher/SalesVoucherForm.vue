<script setup>
import checkPermissions from 'src/composables/checkPermissions'

const endpoint = '/v1/sales-voucher/'

const formData = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/sales-voucher/list/',
})

const { fields, formDefaults, errors, isEdit, loading, submitForm, today } = formData

useMeta(() => ({
  title: `${isEdit.value ? 'Sales Invoice Update' : 'Sales Invoice Add'} | Awecount`,
}))

const onSubmitClick = async (status) => {
  const originalStatus = fields.value.status
  fields.value.status = status
  const data = await submitForm()
  if (data && data.hasOwnProperty('error')) {
    fields.value.status = originalStatus
  }
}
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>
            Update Sale Invoice | {{ fields.status }}
            <span v-if="fields.voucher_no">| # {{ fields.voucher_no }}</span>
          </span>
        </div>
      </q-card-section>
      <SalesVoucherFormFields
        v-model:errors="errors"
        v-model:fields="fields"
        :form-defaults="formDefaults"
        :is-edit="isEdit"
        :today="today"
      />

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          v-if="!isEdit && checkPermissions('SalesCreate')"
          color="orange-8"
          data-testid="issue-btn"
          label="Save Draft"
          type="submit"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
        />
        <q-btn
          v-if="isEdit && fields.status === 'Draft' && checkPermissions('SalesModify')"
          color="orange-8"
          data-testid="draft-btn"
          type="submit"
          :label="isEdit ? 'Update Draft' : 'Save Draft'"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
        />
        <q-btn
          v-if="checkPermissions('SalesCreate')"
          color="green"
          data-testid="create/update-btn"
          :label="
            isEdit
              ? fields?.status === 'Issued' ? 'Update'
                : fields?.status === 'Draft' ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft`
                  : 'update'
              : `Issue # ${formDefaults.options?.voucher_no || 1}`
          "
          :loading="loading"
          @click.prevent="
            () =>
              onSubmitClick(
                isEdit
                  ? fields.status === 'Draft'
                    ? 'Issued'
                    : fields.status
                  : 'Issued',
              )
          "
        />
      </div>
    </q-card>
  </q-form>
</template>
