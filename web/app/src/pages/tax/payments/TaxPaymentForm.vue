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
            <q-select v-model="fields.tax_scheme" label="Tax *" class="col-12 col-md-6"
              :options="formDefaults.collections?.tax_schemes" option-value="id" option-label="name" map-options
              emit-value :error="!!errors.tax_scheme" :error-message="errors.tax_scheme"></q-select>
            <q-input v-model="fields.amount" label="Amount *" class="col-12 col-md-6" :error-message="errors.amount"
              :error="!!errors.amount" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <q-select v-model="fields.cr_account" label="Paid From/By *" class="col-12 col-md-6"
              :options="formDefaults.collections?.cr_accounts" option-value="id" option-label="name" map-options
              emit-value :error="!!errors.cr_account" :error-message="errors.cr_account"></q-select>
          </div>
          <q-input v-model="fields.remarks" type="textarea" autogrow label="Remarks" class="col-12 q-mt-sm"
            :error="!!errors.remarks" :error-message="errors.remarks" />
        </q-card-section>
        <div class="q-pb-lg row justify-end q-gutter-x-md">
          <span v-if="fields.status !== 'Cancelled' && fields.status !== 'Paid'" class="row q-gutter-x-md">
            <q-btn v-if="checkPermissions('TaxPaymentCreate')" @click.prevent="submitWithStatus('Draft', submitForm)"
              color="orange-6" label="Save Draft" class="q-px-lg q-mb-sm" type="submit" :loading="loading" />
            <q-btn v-if="!!fields.status && isEdit && checkPermissions('TaxPaymentCancel')"
              @click.prevent="isDeleteOpen = true" color="red-6" label="Cancel" icon="cancel" class="q-px-lg q-mb-sm"
              :loading="loading" />
            <q-btn v-if="checkPermissions('TaxPaymentCreate')" @click.prevent="submitWithStatus('Paid', submitForm)"
              color="green-6" :label="'Mark as paid'" class="q-px-lg q-mb-sm" :loading="loading" />
          </span>
          <span v-if="fields.status === 'Paid' || fields.status === 'Cancelled'" class="row q-gutter-x-md">
            <q-btn v-if="fields.status !== 'Cancelled'" @click.prevent="isDeleteOpen = true" color="red-6" label="Cancel"
              :loading="loading" icon="cancel" class="q-px-lg q-mb-sm" />
            <q-btn @click.prevent="
              submitWithStatus(
                fields.status === 'Cancelled' ? 'Cancelled' : 'Paid',
                submitForm
              )
              " color="green-6" :label="'Update'" class="q-px-lg q-mb-sm" :loading="loading" />
          </span>
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
            Are you sure?
          </div>
          <div class=" text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)"></q-btn>
              <q-btn flat class="text-red" label="Yes" @click="submitWithStatus('Cancelled')"></q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/tax-payments/'
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
    const isDeleteOpen = ref(false)
    formData.fields.value.date = formData.today
    formData.fields.value.recoverable = false
    async function submitWithStatus(status) {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try { await formData.submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    return {
      ...formData,
      submitWithStatus,
      checkPermissions,
      isDeleteOpen
    }
  },
}
</script>
