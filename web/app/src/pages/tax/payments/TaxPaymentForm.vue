<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/tax-payments/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/tax/payments`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Tax Payment Update' : 'Tax Payment Add'} | Awecount`,
      }
    })
    const isDeleteOpen = ref(false)
    formData.fields.value.date = formData.today
    formData.fields.value.recoverable = false
    async function submitWithStatus(status) {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    return {
      ...formData,
      submitWithStatus,
      checkPermissions,
      isDeleteOpen,
    }
  },
}
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
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
            <q-input
              v-model="fields.voucher_no"
              class="col-12 col-md-6"
              label="Voucher No."
              :error="!!errors.voucher_no"
              :error-message="errors.voucher_no"
            />
            <date-picker
              v-model="fields.date"
              class="col-12 col-md-6"
              label="Date"
              :error="!!errors?.date"
              :error-message="errors?.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.tax_scheme"
              emit-value
              map-options
              class="col-12 col-md-6"
              label="Tax *"
              option-label="name"
              option-value="id"
              :error="!!errors.tax_scheme"
              :error-message="errors.tax_scheme"
              :options="formDefaults.collections?.tax_schemes"
            />
            <q-input
              v-model="fields.amount"
              class="col-12 col-md-6"
              label="Amount *"
              type="number"
              :error="!!errors.amount"
              :error-message="errors.amount"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.cr_account"
                emit-value
                map-options
                label="Paid From/By *"
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/tax-payments/create-defaults/cr_accounts`"
                :error="!!errors.cr_account"
                :error-message="errors.cr_account"
                :options="formDefaults.collections?.cr_accounts"
                :static-option="fields.selected_cr_account_obj"
              />
            </div>
          </div>
          <q-input
            v-model="fields.remarks"
            autogrow
            class="col-12 q-mt-sm"
            label="Remarks"
            type="textarea"
            :error="!!errors.remarks"
            :error-message="errors.remarks"
          />
        </q-card-section>
        <div class="q-pb-lg row justify-end q-gutter-x-md">
          <span v-if="fields.status !== 'Cancelled' && fields.status !== 'Paid'" class="row q-gutter-x-md">
            <q-btn
              v-if="checkPermissions('taxpayment.create')"
              class="q-px-lg q-mb-sm"
              color="orange-6"
              label="Save Draft"
              type="submit"
              :loading="loading"
              @click.prevent="submitWithStatus('Draft', submitForm)"
            />
            <q-btn
              v-if="!!fields.status && isEdit && checkPermissions('taxpayment.cancel')"
              class="q-px-lg q-mb-sm"
              color="red-6"
              icon="cancel"
              label="Cancel"
              :loading="loading"
              @click.prevent="isDeleteOpen = true"
            />
            <q-btn
              v-if="checkPermissions('taxpayment.create')"
              class="q-px-lg q-mb-sm"
              color="green-6"
              label="Mark as paid"
              :loading="loading"
              @click.prevent="submitWithStatus('Paid', submitForm)"
            />
          </span>
          <span v-if="fields.status === 'Paid' || fields.status === 'Cancelled'" class="row q-gutter-x-md">
            <q-btn
              v-if="fields.status !== 'Cancelled'"
              class="q-px-lg q-mb-sm"
              color="red-6"
              icon="cancel"
              label="Cancel"
              :loading="loading"
              @click.prevent="isDeleteOpen = true"
            />
            <q-btn
              class="q-px-lg q-mb-sm"
              color="green-6"
              label="Update"
              :loading="loading"
              @click.prevent="submitWithStatus(fields.status === 'Cancelled' ? 'Cancelled' : 'Paid', submitForm)"
            />
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
          <q-btn
            v-close-popup
            dense
            flat
            round
            class="text-red-700 bg-slate-200 opacity-95"
            icon="close"
          />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
            Are you sure?
          </div>
          <div class="text-blue">
            <div class="row justify-end">
              <q-btn
                flat
                class="q-mr-md text-blue-grey-9"
                label="NO"
                @click="() => (isDeleteOpen = false)"
              />
              <q-btn
                flat
                class="text-red"
                label="Yes"
                @click="submitWithStatus('Cancelled')"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
