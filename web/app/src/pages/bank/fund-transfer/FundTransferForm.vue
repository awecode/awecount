<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/fund-transfer/`
    const isDeleteOpen = ref(false)
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/fund-transfer/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Funds Transfer' : 'Add Funds Transfer'} | Awecount`,
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today
    onMounted(() => {
      if (route.query && route.query.template) {
        let template
        try {
          template = JSON.parse(decodeURIComponent(route.query.template))
        } catch (e) {
          console.log('error parsing data')
        }
        if (!template) return
        if (template.from_account) {
          formData.fields.value.from_account = template.from_account
        }
        if (template.to_account) formData.fields.value.to_account = template.to_account
        if (template.transaction_fee_account) {
          formData.fields.value.transaction_fee_account = template.transaction_fee_account
        }
        if (template.transaction_fee) {
          formData.fields.value.transaction_fee = template.transaction_fee
        }
        if (template.selected_from_account_obj) {
          formData.fields.value.selected_from_account_obj = template.selected_from_account_obj
        }
        if (template.selected_to_account_obj) {
          formData.fields.value.selected_to_account_obj = template.selected_to_account_obj
        }
        if (template.selected_transaction_fee_account_obj) {
          formData.fields.value.selected_transaction_fee_account_obj
            = template.selected_transaction_fee_account_obj
        }
      }
    })
    return {
      ...formData,
      checkPermissions,
      isDeleteOpen,
    }
  },
}
</script>

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
            <q-input
              v-model="fields.voucher_no"
              label="Voucher No."
              class="col-12 col-md-6"
              :error-message="errors.voucher_no"
              :error="!!errors.voucher_no"
            />
            <date-picker
              v-model="fields.date"
              class="col-12 col-md-6"
              label="Date *"
              :error-message="errors.date"
              :error="!!errors.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.from_account"
                :options="formDefaults.collections?.from_account"
                :endpoint="`v1/${route.params.company}/fund-transfer/create-defaults/from_account`"
                :static-option="fields.selected_from_account_obj"
                label="From Account *"
                :error="errors?.from_account"
              />
            </div>
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.to_account"
                :options="formDefaults.collections?.to_account"
                :endpoint="`v1/${route.params.company}/fund-transfer/create-defaults/to_account`"
                :static-option="fields.selected_to_account_obj"
                label="To Account *"
                :error="errors?.to_account"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.amount"
              label="Amount *"
              class="col-12 col-md-6"
              :error-message="errors.amount"
              :error="!!errors.amount"
            />
          </div>
          <div class="text-bold text-lg text-grey-8 q-mt-xl">
            Transaction Fees
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.transaction_fee_account"
                endpoint="v1/fund-transfer/create-defaults/transaction_fee_account"
                :static-option="fields.selected_transaction_fee_account_obj"
                :options="formDefaults.collections?.transaction_fee_account"
                label="Fees Account"
                :error="errors?.transaction_fee_account"
              />
            </div>
            <q-input
              v-model="fields.transaction_fee"
              label="Fees Amount"
              type="number"
              class="col-12 col-md-6"
              :error-message="errors.transaction_fee"
              :error="!!errors.transaction_fee"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('FundTransferCreate') && !isEdit"
            color="green"
            :loading="loading"
            label="Create"
            type="submit"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('FundTransferModify') && isEdit"
            color="green"
            :loading="loading"
            label="Update"
            type="submit"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="fields?.status == 'Issued' && checkPermissions('FundTransferCancel')"
            :loading="loading"
            icon="block"
            color="red"
            label="Cancel"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="fields?.status == 'Issued'"
            :to="`/journal-entries/fund-transfer/${id}/`"
            color="blue"
            :loading="loading"
            icon="library_books"
            label="Journal Entries"
            class="text-h7 q-py-sm"
          />
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
            Are you sure?
          </div>
          <div class=" text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)" />
              <q-btn flat class="text-red" label="Yes" @click="cancelForm" />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
