<script setup>
import checkPermissions from 'src/composables/checkPermissions'

const endpoint = '/v1/purchase-vouchers/'

const { fields, errors, formDefaults, loading, isEdit, today, submitForm } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/purchase-voucher/list/',
})

useMeta(() => {
  return {
    title: `${isEdit?.value ? 'Update Purchases/Expenses' : 'Add Purchases/Expenses'} | Awecount`,
  }
})

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
        <div class="text-h6">
          <span v-if="!isEdit">New Purchase / Expense</span>
          <span v-else>Update Purchase / Expense</span>
        </div>
      </q-card-section>

      <PurchaseVoucherFormFields
        v-model:errors="errors"
        v-model:fields="fields"
        :form-defaults="formDefaults"
        :is-edit="isEdit"
        :today="today"
      />

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          v-if="checkPermissions('PurchaseVoucherCreate') && !isEdit"
          color="orange"
          label="Save Draft"
          type="submit"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <q-btn
          v-if="checkPermissions('PurchaseVoucherCreate') && isEdit && fields.status === 'Draft'"
          color="orange"
          label="Update Draft"
          type="submit"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <q-btn
          v-if="checkPermissions('PurchaseVoucherCreate') && !isEdit"
          color="green"
          label="Issue"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Issued')"
        />
        <q-btn
          v-if="checkPermissions('PurchaseVoucherCreate') && isEdit"
          color="green"
          :label="fields.status === 'Draft' ? 'Issue from Draft' : 'Update'"
          :loading="loading"
          @click.prevent="() => onSubmitClick(fields.status === 'Draft' ? 'Issued' : fields.status)"
        />
      </div>
    </q-card>
  </q-form>
</template>
