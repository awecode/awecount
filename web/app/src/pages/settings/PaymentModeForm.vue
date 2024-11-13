<template>
  <q-form class="q-pa-lg" @submit.prevent="submitForm" v-if="fields">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">Payment Mode</div>
      </q-card-section>

      <q-card-section>
        <div class="row q-col-gutter-md">
          <!-- Basic Information -->
          <div class="col-12 col-md-6">
            <q-input
              v-model="fields.name"
              label="Name"
              :rules="[v => !!v || 'Name is required']"
              filled
            />
          </div>

          <div class="col-12 col-md-6">
            <n-auto-complete-v2
              v-model="fields.account"
              label="Account"
              :options="formDefaults?.collections?.accounts"
              :staticOption="isEdit ? fields.selected_account_obj : null"
              endpoint="v1/payment-modes/create-defaults/accounts"
              option-value="id"
              option-label="name"
              :rules="[v => !!v || 'Account is required']"
              filled
            />
          </div>

          <div class="col-12 col-md-6">
            <q-checkbox
              v-model="fields.enabled_for_sales"
              label="Enable for Sales"
            />
          </div>

          <div class="col-12 col-md-6">
            <q-checkbox
              v-model="fields.enabled_for_purchase"
              label="Enable for Purchase"
            />
          </div>

          <div class="col-12">
            <q-checkbox
              v-model="hasTransactionFee"
              label="Transaction Fee?"
              @update:model-value="onTransactionFeeToggle"
            />
          </div>

          <!-- Transaction Fee Configuration -->
          <div class="col-12" v-if="hasTransactionFee">
            <q-card>
                <q-card-section>
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-6">
                      <q-select
                        v-model="fields.transaction_fee_config.type"
                        :options="feeTypeOptions"
                        label="Fee Type"
                        filled
                        map-options
                        @update:model-value="onFeeTypeChange"
                      />
                    </div>

                    <template v-if="fields.transaction_fee_config.type">
                    <div class="col-12 col-md-6">
                      <n-auto-complete-v2
                        v-model="fields.transaction_fee_account"
                        label="Transaction Fee Account"
                        :options="formDefaults?.collections?.accounts"
                        :staticOption="isEdit ? fields.selected_transaction_fee_account_obj : null"
                        endpoint="v1/ledger/accounts"
                        option-value="id"
                        option-label="name"
                        :rules="[v => !fields.transaction_fee_config || !!v || 'Fee account is required when fee is enabled']"
                        filled
                      />
                    </div>

                    <!-- Fixed Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'fixed'">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model.number="fields.transaction_fee_config.value"
                          label="Fixed Amount"
                          type="number"
                          step="any"
                          filled
                          :rules="[v => v > 0 || 'Amount must be greater than 0']"
                        />
                      </div>
                    </template>

                    <!-- Percentage Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'percentage'">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model.number="fields.transaction_fee_config.value"
                          label="Percentage"
                          type="number"
                          step="any"
                          filled
                          :rules="[
                            v => v > 0 || 'Percentage must be greater than 0',
                            v => v <= 100 || 'Percentage must be less than or equal to 100'
                          ]"
                        />
                      </div>
                    </template>

                    <!-- Slab Based Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'slab_based'">
                      <div class="col-12">
                        <div class="text-subtitle2 q-mb-sm">Fee Slabs</div>
                        <div v-for="(slab, index) in fields.transaction_fee_config.slabs" :key="index" class="row q-col-gutter-sm q-mb-md">
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.min_amount"
                              label="Min Amount"
                              type="number"
                              step="any"
                              filled
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.max_amount"
                              label="Max Amount"
                              type="number"
                              step="any"
                              filled
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.rate"
                              label="Rate (%)"
                              type="number"
                              step="any"
                              filled
                            />
                          </div>
                          <div class="col-12 col-md-3 flex items-center">
                            <q-btn
                              flat
                              round
                              color="negative"
                              icon="delete"
                              @click="removeSlab(index)"
                            />
                          </div>
                        </div>
                        <q-btn
                          color="primary"
                          label="Add Slab"
                          @click="addSlab"
                          class="q-mb-md"
                        />
                      </div>
                    </template>

                    <!-- Fee Limits -->
                    <div class="col-12">
                      <div class="text-subtitle2 q-mb-sm">Fee Limits</div>

                      <div class="row q-col-gutter-md">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model.number="fields.transaction_fee_config.min_fee"
                          label="Minimum Fee"
                          type="number"
                          step="any"
                          filled
                        />
                      </div>
                      <div class="col-12 col-md-6">
                      <q-input
                        v-model.number="fields.transaction_fee_config.max_fee"
                        label="Maximum Fee"
                        type="number"
                        step="any"
                        filled
                      />
                      </div>
                      </div>
                    </div>
                    <!-- Extra Fee -->
                    <div class="col-12">
                      <q-checkbox
                        v-model="hasExtraFee"
                        label="Add Extra Fee"
                        @update:model-value="onExtraFeeToggle"
                      />
                    </div>

                    <template v-if="hasExtraFee && fields.transaction_fee_config.extra_fee">
                      <div class="col-12 col-md-4">
                        <q-select
                          v-model="fields.transaction_fee_config.extra_fee.type"
                          :options="extraFeeTypeOptions"
                          label="Extra Fee Type"
                          filled
                          map-options
                        />
                      </div>
                      <div class="col-12 col-md-4">
                        <q-input
                          v-model.number="fields.transaction_fee_config.extra_fee.value"
                          :label="fields.transaction_fee_config.extra_fee.type === 'fixed' ? 'Amount' : 'Percentage'"
                          type="number"
                          step="any"
                          filled
                        />
                      </div>
                    </template>
                    </template>
                  </div>

                </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          color="red"
          @click="cancel"
          label="Cancel"
        />
        <q-btn
          type="submit"
          color="primary"
          :loading="loading"
          label="Save"
        />
      </q-card-actions>
    </q-card>
  </q-form>
</template>

<script setup>
import { ref } from 'vue'


const { fields, errors, formDefaults, isEdit, submitForm, cancel, cancelForm, loading } = useForm('v1/payment-modes/', {
  getDefaults: true,
  successRoute: '/settings/payment-mode/list/',
})

fields.value.enabled_for_sales = true
fields.value.enabled_for_purchase = true
fields.value.account = null
fields.value.transaction_fee_account = null


const hasTransactionFee = ref(false)
watch(() => fields.value.transaction_fee_config, (value) => {
  hasTransactionFee.value = !!value
}, { immediate: true })


const hasExtraFee = ref(false)

const onTransactionFeeToggle = (value) => {
  if (!!fields.value.transaction_fee_config) {
    return
  }

  if (value) {
    fields.value.transaction_fee_config = {
      type: 'fixed',
      value: 0,
      min_fee: 0,
      max_fee: 0,
      extra_fee: null
    }
  } else {
    fields.value.transaction_fee_config = null
  }
}

const feeTypeOptions = [
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' },
  { label: 'Slab Based', value: 'slab_based' },
  { label: 'Sliding Scale', value: 'sliding_scale' }
]

const extraFeeTypeOptions = [
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' }
]

const onFeeTypeChange = (type) => {
  if (type.value === null) {
    fields.value.transaction_fee_config = null
    return
  }
  fields.value.transaction_fee_config = {
    type: type.value,
    ...(type.value === 'slab_based' ? { slabs: [] } : { value: 0 })
  }
  if (type.value === 'slab_based') {
    addSlab()
  }
}

const onExtraFeeToggle = (value) => {
  if (value) {
    fields.value.transaction_fee_config.extra_fee = {
      type: 'fixed',
      value: 0
    }
  } else {
    fields.value.transaction_fee_config.extra_fee = null
  }
}

const addSlab = () => {
  if (!fields.value.transaction_fee_config.slabs) return

  const lastSlab = fields.value.transaction_fee_config.slabs[fields.value.transaction_fee_config.slabs.length - 1]
  const minAmount = lastSlab ? lastSlab.max_amount || 0 : 0

  fields.value.transaction_fee_config.slabs.push({
    min_amount: minAmount,
    max_amount: minAmount + 1000,
    rate: 0
  })
}

const removeSlab = (index) => {
  if (!fields.value.transaction_fee_config.slabs) return
  fields.value.transaction_fee_config.slabs.splice(index, 1)

  // Adjust the min_amount of the next slab if it exists
  if (fields.value.transaction_fee_config.slabs[index]) {
    const previousSlab = fields.value.transaction_fee_config.slabs[index - 1]
    fields.value.transaction_fee_config.slabs[index].min_amount = previousSlab ? previousSlab.max_amount || 0 : 0
  }
}

</script>
