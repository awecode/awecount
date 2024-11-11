<template>
  <q-form class="q-pa-lg" @submit.prevent="onSubmit" v-if="fields">
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
              :options="accountOptions"
              endpoint="v1/ledger/accounts"
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

          <!-- Transaction Fee Configuration -->
          <div class="col-12">
            <q-card>
              <q-card-section
                class="bg-grey text-white"
              >
                <div class="text-h6">Transaction Fee Configuration</div>
              </q-card-section>
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
                        :options="accountOptions"
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
                              filled
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.max_amount"
                              label="Max Amount"
                              type="number"
                              filled
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.rate"
                              label="Rate (%)"
                              type="number"
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
                          filled
                        />
                      </div>
                      <div class="col-12 col-md-6">
                      <q-input
                        v-model.number="fields.transaction_fee_config.max_fee"
                        label="Maximum Fee"
                        type="number"
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
          type="submit"
          color="primary"
          :loading="loading"
          label="Save"
        />
      </q-card-actions>
    </q-card>
  </q-form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'

// @ts-expect-error not typed
import useApi from '/src/composables/useApi'

interface PaymentModeFields {
  id?: number
  name: string
  enabled_for_sales: boolean
  enabled_for_purchase: boolean
  account: number | null
  transaction_fee_config: {
    type: string | null
    value?: number
    slabs?: Array<{
      min_amount: number
      max_amount?: number
      rate: number
    }>
    min_fee?: number
    max_fee?: number
    extra_fee?: {
      type: string
      value: number
    }
  }
  transaction_fee_account: number | null
}

const $q = useQuasar()
const loading = ref(false)
const hasExtraFee = ref(false)

const fields = ref<PaymentModeFields>({
  name: '',
  enabled_for_sales: true,
  enabled_for_purchase: true,
  account: null,
  transaction_fee_account: null,
  transaction_fee_config: {
    type: 'fixed',
    value: 0
  }
})

const feeTypeOptions = [
  { label: 'None', value: null },
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' },
  { label: 'Slab Based', value: 'slab_based' },
  { label: 'Sliding Scale', value: 'sliding_scale' }
]

const extraFeeTypeOptions = [
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' }
]

const accountOptions = computed(() => ({
  results: [],
  pagination: {}
}))

const onFeeTypeChange = (type: { label: string; value: string }) => {
  if (type.value === null ) {
    fields.value.transaction_fee_config = { type: null }
    return
  }
  fields.value.transaction_fee_config = {
    type: type.value,
    ...(type.value === 'slab_based' ? { slabs: [] } : { value: 0 })
  }
  console.log(fields.value.transaction_fee_config)
}

const onExtraFeeToggle = (value: boolean) => {
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

const removeSlab = (index: number) => {
  if (!fields.value.transaction_fee_config.slabs) return
  fields.value.transaction_fee_config.slabs.splice(index, 1)

  // Adjust the min_amount of the next slab if it exists
  if (fields.value.transaction_fee_config.slabs[index]) {
    const previousSlab = fields.value.transaction_fee_config.slabs[index - 1]
    fields.value.transaction_fee_config.slabs[index].min_amount = previousSlab ? previousSlab.max_amount || 0 : 0
  }
}

const onSubmit = async () => {
  try {
    loading.value = true
    const endpoint = fields.value.id
      ? `v1/payment-modes/${fields.value.id}/`
      : 'v1/payment-modes/'

    const method = fields.value.id ? 'PUT' : 'POST'

    const response = await useApi(endpoint, {
      method,
      body: fields.value
    })

    $q.notify({
      color: 'positive',
      message: 'Payment mode saved successfully',
      icon: 'check'
    })

    // Emit save event or handle navigation
  } catch (error: any) {
    $q.notify({
      color: 'negative',
      message: error.data?.message || 'An error occurred while saving',
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Optionally fetch existing payment mode data if editing
const fetchPaymentMode = async (id: number) => {
  try {
    const data = await useApi(`v1/payment-modes/${id}/`)
    fields.value = data
    hasExtraFee.value = !!data.transaction_fee_config.extra_fee
  } catch (error) {
    $q.notify({
      color: 'negative',
      message: 'Failed to fetch payment mode data',
      icon: 'error'
    })
  }
}
</script>