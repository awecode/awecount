<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Fund Transfer</span>
          <span v-else>Update Fund Transfer</span>
        </div>
      </q-card-section>
      <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.voucher_no" label="Voucher No." class="col-12 col-md-6"
              :error-message="errors.voucher_no" :error="!!errors.voucher_no" />
            <date-picker v-model="fields.date" class="col-12 col-md-6" label="Date *" :error-message="errors.date"
              :error="!!errors.date"></date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete v-model="fields.from_account" :options="formDefaults.collections?.from_account"
                label="From Account *" :error="errors?.from_account" />
            </div>
            <div class="col-12 col-md-6">
              <n-auto-complete v-model="fields.to_account" :options="formDefaults.collections?.to_account"
                label="To Account *" :error="errors?.to_account" />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.amount" label="Amount *" class="col-12 col-md-6" :error-message="errors.amount"
              :error="!!errors.amount" />
          </div>
          <div class="text-bold text-lg text-grey-8 q-mt-xl">
            Transaction Fees
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete v-model="fields.transaction_fee_account"
                :options="formDefaults.collections?.transaction_fee_account" label="Fees Account"
                :error="errors?.transaction_fee_account" />
            </div>
            <q-input v-model="fields.transaction_fee" label="Fees Amount" type="number" class="col-12 col-md-6"
              :error-message="errors.transaction_fee" :error="!!errors.transaction_fee" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('FundTransferCreate') && !isEdit" @click.prevent="submitForm" color="green"
            label="Create" class="q-ml-auto" type="submit" />
          <q-btn v-if="checkPermissions('FundTransferModify') && isEdit" @click.prevent="submitForm" color="green"
            label="Update" class="q-ml-auto" type="submit" />
          <q-btn v-if="fields?.status == 'Issued' && checkPermissions('FundTransferCancel')" @click.prevent="cancelForm"
            icon="block" color="red" :label="'Cancel'" class="q-ml-md" />
          <q-btn v-if="fields?.status == 'Issued'" :to="`/journal-entries/fund-transfer/${id}/`" color="blue"
            icon="library_books" label="Journal Entries" class="text-h7 q-py-sm q-ml-md" />
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
    const endpoint = '/v1/fund-transfer/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/fund-transfer/list/',
    })
    const route = useRoute()
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Update Funds Transfer'
            : 'Add Funds Transfer') + ' | Awecount',
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today

    // TODO: Should Test this
    onMounted(() => {
      if (route.params && route.params.template) {
        const template = route.params.template
        if (template.from_account)
          formData.fields.value.from_account = template.from_account
        if (template.to_account) formData.fields.value.to_account = template.to_account
        if (template.transaction_fee_account)
          formData.fields.value.transaction_fee_account = template.transaction_fee_account
        if (template.transaction_fee)
          formData.fields.value.transaction_fee = template.transaction_fee
      }
    })
    return {
      ...formData,
      checkPermissions
    }
  },
}
</script>
