<template>
  <q-form class="q-pa-lg" v-if="fields" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!fields.id">New Tax Payment</span>
          <span v-else>Update</span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.voucher_no" label="Voucher No." class="col-12 col-md-6"
              :error-message="errors.voucher_no" :error="!!errors.voucher_no" />
            <date-picker v-model="fields.date" class="col-12 col-md-6" label="Date" :error-message="errors?.date"
              :error="!!errors?.date">
            </date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <q-select v-model="fields.tax_scheme" label="Tax" class="col-12 col-md-6"
              :options="formDefaults.collections?.tax_schemes" option-value="id" option-label="name" map-options
              emit-value :error="!!errors.tax_scheme" :error-message="errors.tax_scheme"></q-select>
            <q-input v-model="fields.amount" label="Amount" class="col-12 col-md-6" :error-message="errors.amount"
              :error="!!errors.amount" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <q-select v-model="fields.cr_account" label="Paid From/By *" class="col-12 col-md-6"
              :options="formDefaults.collections?.cr_accounts" option-value="id" option-label="name" map-options
              emit-value :error="!!errors.tax_scheme" :error-message="errors.tax_scheme"></q-select>
          </div>
          <q-input v-model="fields.remarks" type="textarea" autogrow label="Remarks" class="col-12 q-mt-sm"
            :error="!!errors.remarks" :error-message="errors.remarks" />
        </q-card-section>
        <div class="q-pb-lg row justify-start q-gutter-x-md">
          <span v-if="fields.status !== 'Cancelled' && fields.status !== 'Paid'" class="row q-gutter-x-md">
            <q-btn v-if="checkPermissions('TaxPaymentCreate')" @click.prevent="submitWithStatus('Draft', submitForm)"
              color="orange-6" label="Save Draft" class="q-px-lg q-mb-sm" type="submit" />
            <q-btn v-if="!!fields.status && isEdit && checkPermissions('TaxPaymentCancel')" @click.prevent="onCancelClick"
              color="red-6" label="Cancel" icon="cancel" class="q-px-lg q-mb-sm" />
            <q-btn v-if="checkPermissions('TaxPaymentCreate')" @click.prevent="submitWithStatus('Paid', submitForm)"
              color="green-6" :label="'Mark as paid'" class="q-px-lg q-mb-sm" />
          </span>
          <span v-if="fields.status === 'Paid' || fields.status === 'Cancelled'" class="row q-gutter-x-md">
            <q-btn @click.prevent="
              submitWithStatus(
                fields.status === 'Cancelled' ? 'Cancelled' : 'Paid',
                submitForm
              )
              " color="green-6" :label="'Update'" class="q-px-lg q-mb-sm" />
            <q-btn v-if="fields.status !== 'Cancelled'" @click.prevent="onCancelClick" color="red-6" label="Cancel"
              icon="cancel" class="q-px-lg q-mb-sm" />
          </span>
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
import { useQuasar } from 'quasar'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/tax-payments/'
    const $q = useQuasar()
    // const router = useRouter()
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/tax-payment/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Tax Payment Update' : 'Tax Payment Add') +
          ' | Awecount',
      }
    })
    formData.fields.value.date = formData.today
    formData.fields.value.recoverable = false
    async function submitWithStatus(status, submitForm) {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try { await formData.submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    const onCancelClick = async () => {
      $q.dialog({
        title: '<span class="text-red">Delete?</span>',
        message: 'Are you sure you want to delete?',
        cancel: true,
        html: true,
      }).onOk(() => {
        submitWithStatus('Cancelled')
      })
    }
    return {
      ...formData,
      submitWithStatus,
      checkPermissions,
      onCancelClick
    }
  },
}
</script>
