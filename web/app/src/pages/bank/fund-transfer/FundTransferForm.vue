<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Fund Transfer</span>
          <span v-else>Update Fund Transfer</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.voucher_no"
              label="Voucher No."
              class="col-6"
              :error-message="errors.voucher_no"
              :error="!!errors.voucher_no"
            />
            <q-input
              v-model="fields.date"
              class="col-6"
              label="Date *"
              :error-message="errors.date"
              :error="!!errors.date"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date v-model="fields.date" today-btn mask="YYYY-MM-DD">
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <div class="col-6">
              <n-auto-complete
                v-model="fields.from_account"
                :options="formDefaults.collections?.from_account"
                label="From Account *"
                :error="errors?.from_account"
              />
            </div>
            <div class="col-6">
              <n-auto-complete
                v-model="fields.to_account"
                :options="formDefaults.collections?.to_account"
                label="To Account *"
                :error="errors?.to_account"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.amount"
              label="Amount *"
              class="col-6"
              :error-message="errors.amount"
              :error="!!errors.amount"
            />
          </div>
          <div class="text-bold text-lg text-grey-8 q-mt-xl">
            Transaction Fees
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <div class="col-6">
              <n-auto-complete
                v-model="fields.transaction_fee_account"
                :options="formDefaults.collections?.transaction_fee_account"
                label="Fees Account"
                :error="errors?.transaction_fee_account"
              />
            </div>
            <q-input
              v-model="fields.transaction_fee"
              label="Fees Amount"
              type="number"
              class="col-6"
              :error-message="errors.transaction_fee"
              :error="!!errors.transaction_fee"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
          <q-btn
            v-if="fields?.status == 'Issued'"
            @click.prevent="cancelForm"
            icon="block"
            color="red"
            :label="'Cancel'"
            class="q-ml-md"
          />
          <q-btn
            v-if="fields?.status == 'Issued'"
            :to="`/journal-entries/fund-transfer/${id}/`"
            color="blue"
            icon="library_books"
            label="Journal Entries"
            class="text-h7 q-py-sm q-ml-md"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/fund-transfer/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/bank/fund-transfer/',
    })

    formData.fields.value.date = formData.fields.value.date || formData.today

    return {
      ...formData,
    }
  },
}
</script>
