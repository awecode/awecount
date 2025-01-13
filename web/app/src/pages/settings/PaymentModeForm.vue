<script setup>
import { computed, ref } from 'vue'

const useTransactionFeeValidation = () => {
  const validationErrors = ref({})

  const VALID_FEE_TYPES = ['fixed', 'percentage', 'slab_based', 'sliding_scale']
  const VALID_EXTRA_FEE_TYPES = ['fixed', 'percentage']

  const validateFeeConfig = (config) => {
    validationErrors.value = {}

    if (!config) {
      return true
    }

    try {
      if (typeof config !== 'object') {
        validationErrors.value.transaction_fee_config = 'Fee configuration must be an object'
        return false
      }

      if (!config.type) {
        validationErrors.value.transaction_fee_config = 'Fee type must be specified'
        return false
      }

      if (!VALID_FEE_TYPES.includes(config.type)) {
        validationErrors.value.transaction_fee_config = `Invalid fee type: ${config.type}`
        return false
      }

      const validationFunctions = {
        fixed: validateSimpleFee,
        percentage: validateSimpleFee,
        slab_based: validateSlabBased,
        sliding_scale: validateSlidingScale,
      }

      if (!validationFunctions[config.type](config)) {
        return false
      }

      return validateFeeLimits(config)
    } catch (error) {
      validationErrors.value.transaction_fee_config = error.message
      return false
    }
  }

  const validateSimpleFee = (config) => {
    if (!('value' in config)) {
      validationErrors.value.transaction_fee_config = 'Value must be specified'
      return false
    }

    if (config.type === 'percentage' && (config.value < 0 || config.value > 100)) {
      validationErrors.value.transaction_fee_config = 'Percentage must be between 0 and 100'
      return false
    }

    return true
  }

  const validateSlabBased = (config) => {
    if (!config.slabs || !Array.isArray(config.slabs) || config.slabs.length === 0) {
      validationErrors.value.transaction_fee_config = 'Slabs must be specified and non-empty'
      return false
    }

    let prevMax = 0
    const slabErrors = []

    for (let i = 0; i < config.slabs.length; i++) {
      const slab = config.slabs[i]
      const slabError = {}

      // Check required min_amount
      if (!('min_amount' in slab)) {
        slabError.min_amount = 'Minimum amount must be specified'
      } else if (slab.min_amount !== prevMax) {
        slabError.min_amount = 'Slabs must be continuous without gaps'
      }

      // Check fee type (rate or amount, but not both)
      if ('rate' in slab === 'amount' in slab) {
        slabError.fee_type = 'Each slab must specify either rate or amount, but not both'
      }

      // Validate max_amount for all except last slab
      if (i < config.slabs.length - 1) {
        if (!('max_amount' in slab)) {
          slabError.max_amount = 'All slabs except the last must specify maximum amount'
        } else if (slab.max_amount <= slab.min_amount) {
          slabError.max_amount = 'Maximum amount must be greater than minimum amount'
        }
      }

      if (Object.keys(slabError).length > 0) {
        slabErrors[i] = slabError
      }

      prevMax = slab.max_amount || Infinity
    }

    if (slabErrors.length > 0) {
      validationErrors.value.transaction_fee_config = { slabs: slabErrors }
      return false
    }

    return true
  }

  const validateSlidingScale = (config) => {
    if (!config.slabs || !Array.isArray(config.slabs) || config.slabs.length === 0) {
      validationErrors.value.transaction_fee_config = 'Slabs must be specified and non-empty'
      return false
    }

    const slabErrors = []

    for (let i = 0; i < config.slabs.length; i++) {
      const slab = config.slabs[i]
      const slabError = {}

      if (!('min_amount' in slab)) {
        slabError.min_amount = 'Minimum amount must be specified'
      }

      if ('rate' in slab === 'amount' in slab) {
        slabError.fee_type = 'Each slab must specify either rate or amount, but not both'
      }

      if (Object.keys(slabError).length > 0) {
        slabErrors[i] = slabError
      }
    }

    if (slabErrors.length > 0) {
      validationErrors.value.transaction_fee_config = { slabs: slabErrors }
      return false
    }

    return true
  }

  const validateFeeLimits = (config) => {
    if ('min_fee' in config && 'max_fee' in config) {
      if (Number(config.min_fee) > Number(config.max_fee)) {
        validationErrors.value.transaction_fee_config = 'Minimum fee cannot be greater than maximum fee'
        return false
      }
    }

    if (config.extra_fee) {
      if (typeof config.extra_fee !== 'object') {
        validationErrors.value.transaction_fee_config = 'Extra fee must be an object'
        return false
      }

      if (!config.extra_fee.type) {
        validationErrors.value.transaction_fee_config = 'Extra fee type must be specified'
        return false
      }

      if (!VALID_EXTRA_FEE_TYPES.includes(config.extra_fee.type)) {
        validationErrors.value.transaction_fee_config = 'Invalid extra fee type'
        return false
      }

      if (!('value' in config.extra_fee)) {
        validationErrors.value.transaction_fee_config = 'Value must be specified for extra fee'
        return false
      }

      if (config.extra_fee.type === 'percentage' && (config.extra_fee.value < 0 || config.extra_fee.value > 100)) {
        validationErrors.value.transaction_fee_config = 'Extra fee percentage must be between 0 and 100'
        return false
      }
    }

    return true
  }

  return {
    validationErrors: computed(() => validationErrors.value),
    validateFeeConfig,
  }
}

const { fields, errors, formDefaults, isEdit, submitForm, cancel, cancelForm, loading } = useForm('v1/payment-modes/', {
  getDefaults: true,
  successRoute: '/settings/payment-mode/list/',
})

fields.value.enabled_for_sales = true
fields.value.enabled_for_purchase = true
fields.value.account = null
fields.value.transaction_fee_account = null

const { validationErrors, validateFeeConfig } = useTransactionFeeValidation()

const hasTransactionFee = ref(false)
const hasExtraFee = ref(false)

watch(
  () => fields.value.transaction_fee_config,
  (value) => {
    hasTransactionFee.value = !!value

    if (value) {
      hasExtraFee.value = !!value.extra_fee

      validateFeeConfig(value)
      if (value.min_fee === '') {
        delete fields.value.transaction_fee_config.min_fee
      }
      if (value.max_fee === '') {
        delete fields.value.transaction_fee_config.max_fee
      }
    }
  },
  {
    immediate: true,
    deep: true,
  },
)

const onTransactionFeeToggle = (value) => {
  if (fields.value.transaction_fee_config) {
    return
  }

  if (value) {
    fields.value.transaction_fee_config = {
      type: 'fixed',
      value: 0,
      extra_fee: null,
    }
  } else {
    fields.value.transaction_fee_config = null
  }
}

const feeTypeOptions = [
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' },
  { label: 'Slab Based', value: 'slab_based' },
  { label: 'Sliding Scale', value: 'sliding_scale' },
]

const extraFeeTypeOptions = [
  { label: 'Fixed', value: 'fixed' },
  { label: 'Percentage', value: 'percentage' },
]

const slabFeeTypeOptions = [
  { label: 'Rate (%)', value: 'rate' },
  { label: 'Fixed Amount', value: 'amount' },
]

const onFeeTypeChange = (type) => {
  if (type.value === null) {
    fields.value.transaction_fee_config = null
    return
  }

  fields.value.transaction_fee_config = {
    type: type.value,
    ...(type.value === 'slab_based' || type.value === 'sliding_scale' ? { slabs: [] } : { value: 0 }),
  }

  if (type.value === 'slab_based' || type.value === 'sliding_scale') {
    addSlab()
  }
}

const onSlabFeeTypeChange = (index) => {
  const slab = fields.value.transaction_fee_config.slabs[index]
  if (slab.fee_type === 'rate') {
    delete slab.amount
    slab.rate = 0
  } else {
    delete slab.rate
    slab.amount = 0
  }
}

const onExtraFeeToggle = (value) => {
  if (value) {
    fields.value.transaction_fee_config.extra_fee = {
      type: 'fixed',
      value: 0,
    }
  } else {
    fields.value.transaction_fee_config.extra_fee = null
  }
}

const addSlab = () => {
  if (!fields.value.transaction_fee_config.slabs) return

  const lastSlab = fields.value.transaction_fee_config.slabs[fields.value.transaction_fee_config.slabs.length - 1]
  const minAmount = lastSlab ? (fields.value.transaction_fee_config.type === 'slab_based' ? lastSlab.max_amount : lastSlab.min_amount) || 0 : 0

  const newSlab = {
    min_amount: minAmount,
    fee_type: 'rate',
    rate: 0,
  }

  if (fields.value.transaction_fee_config.type === 'slab_based') {
    newSlab.max_amount = minAmount + 1000
  }

  fields.value.transaction_fee_config.slabs.push(newSlab)
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

<template>
  <q-form v-if="fields" class="q-pa-lg" @submit.prevent="submitForm">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          Payment Mode
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row q-col-gutter-md">
          <!-- Basic Information -->
          <div class="col-12 col-md-6">
            <q-input
              v-model="fields.name"
              filled
              label="Name"
              :error="!!errors.name"
              :error-message="errors.name"
              :rules="[(v) => !!v || 'Name is required']"
            />
          </div>

          <div class="col-12 col-md-6">
            <n-auto-complete-v2
              v-model="fields.account"
              filled
              endpoint="v1/payment-modes/create-defaults/accounts"
              label="Account"
              option-label="name"
              option-value="id"
              :error="!!errors.account"
              :error-message="errors.account"
              :options="formDefaults?.collections?.accounts"
              :rules="[(v) => !!v || 'Account is required']"
              :static-option="isEdit ? fields.selected_account_obj : null"
            />
          </div>

          <div class="col-12 col-md-6">
            <q-checkbox
              v-model="fields.enabled_for_sales"
              label="Enable for Sales"
              :error="!!errors.enabled_for_sales"
              :error-message="errors.enabled_for_sales"
            />
          </div>

          <div class="col-12 col-md-6">
            <q-checkbox
              v-model="fields.enabled_for_purchase"
              label="Enable for Purchase"
              :error="!!errors.enabled_for_purchase"
              :error-message="errors.enabled_for_purchase"
            />
          </div>

          <div class="col-12">
            <q-checkbox v-model="hasTransactionFee" label="Transaction Fee?" @update:model-value="onTransactionFeeToggle" />
          </div>

          <!-- Transaction Fee Configuration -->
          <div v-if="hasTransactionFee" class="col-12">
            <q-card>
              <q-card-section>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-select
                      v-model="fields.transaction_fee_config.type"
                      filled
                      map-options
                      label="Fee Type"
                      :options="feeTypeOptions"
                      @update:model-value="onFeeTypeChange"
                    />
                  </div>

                  <template v-if="fields.transaction_fee_config.type">
                    <div class="col-12 col-md-6">
                      <n-auto-complete-v2
                        v-model="fields.transaction_fee_account"
                        filled
                        endpoint="v1/payment-modes/create-defaults/accounts"
                        label="Transaction Fee Account"
                        option-label="name"
                        option-value="id"
                        :error="!!errors.transaction_fee_account"
                        :error-message="errors.transaction_fee_account"
                        :options="formDefaults?.collections?.accounts"
                        :rules="[(v) => !fields.transaction_fee_config || !!v || 'Fee account is required when fee is enabled']"
                        :static-option="isEdit ? fields.selected_transaction_fee_account_obj : null"
                      />
                    </div>

                    <!-- Fixed Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'fixed'">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model.number="fields.transaction_fee_config.value"
                          filled
                          label="Fixed Amount"
                          min="0"
                          step="any"
                          type="number"
                          :rules="[(v) => v > 0 || 'Amount must be greater than 0']"
                        />
                      </div>
                    </template>

                    <!-- Percentage Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'percentage'">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model.number="fields.transaction_fee_config.value"
                          filled
                          label="Percentage"
                          min="0"
                          step="any"
                          type="number"
                          :rules="[(v) => v > 0 || 'Percentage must be greater than 0', (v) => v <= 100 || 'Percentage must be less than or equal to 100']"
                        />
                      </div>
                    </template>

                    <!-- Slab Based Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'slab_based' || fields.transaction_fee_config.type === 'sliding_scale'">
                      <div class="col-12">
                        <div class="text-subtitle2 q-mb-sm">
                          {{ fields.transaction_fee_config.type === 'slab_based' ? 'Fee Slabs' : 'Sliding Scale Slabs' }}
                        </div>
                        <div v-for="(slab, index) in fields.transaction_fee_config.slabs" :key="index" class="row q-col-gutter-sm q-mb-md">
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.min_amount"
                              filled
                              label="Min Amount"
                              min="0"
                              step="any"
                              type="number"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.min_amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.min_amount"
                              :rules="[(v) => v >= 0 || 'Minimum amount must be greater than or equal to 0']"
                            />
                          </div>
                          <div v-if="fields.transaction_fee_config.type === 'slab_based'" class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.max_amount"
                              filled
                              label="Max Amount"
                              min="0"
                              step="any"
                              type="number"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.max_amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.max_amount"
                              :rules="[(v) => v >= 0 || 'Maximum amount must be greater than or equal to 0']"
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-select
                              v-model="slab.fee_type"
                              emit-value
                              filled
                              map-options
                              label="Fee Type"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.fee_type"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.fee_type"
                              :options="slabFeeTypeOptions"
                              @update:model-value="onSlabFeeTypeChange(index)"
                            />
                          </div>
                          <div class="col-12 col-md-2">
                            <q-input
                              v-if="slab.fee_type === 'rate'"
                              v-model.number="slab.rate"
                              filled
                              label="Rate (%)"
                              min="0"
                              step="any"
                              type="number"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.rate"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.rate"
                              :rules="[(v) => v >= 0 || 'Rate must be greater than or equal to 0', (v) => v <= 100 || 'Rate must be less than or equal to 100']"
                            />
                            <q-input
                              v-else
                              v-model.number="slab.amount"
                              filled
                              label="Fixed Amount"
                              min="0"
                              step="any"
                              type="number"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.amount"
                              :rules="[(v) => v >= 0 || 'Amount must be greater than or equal to 0']"
                            />
                          </div>
                          <div class="col-12 col-md-1 flex items-center">
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
                          class="q-mb-md"
                          color="primary"
                          :label="`Add ${fields.transaction_fee_config.type === 'slab_based' ? 'Slab' : 'Scale'}`"
                          @click="addSlab"
                        />
                      </div>
                    </template>

                    <!-- Fee Limits -->
                    <div class="col-12">
                      <div class="text-subtitle2 q-mb-sm">
                        Fee Limits
                      </div>

                      <div class="row q-col-gutter-md">
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model.number="fields.transaction_fee_config.min_fee"
                            filled
                            label="Minimum Fee"
                            min="0"
                            step="any"
                            type="number"
                            :rules="[
                              (v) => {
                                if (v && v < 0) {
                                  return 'Minimum fee must be greater than or equal to 0'
                                }
                                if (v && fields.transaction_fee_config.max_fee && v > fields.transaction_fee_config.max_fee) {
                                  return 'Minimum fee must be less than or equal to maximum fee'
                                }
                                return true
                              },
                            ]"
                          />
                        </div>
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model.number="fields.transaction_fee_config.max_fee"
                            filled
                            label="Maximum Fee"
                            min="0"
                            step="any"
                            type="number"
                            :rules="[
                              (v) => {
                                if (v && v < 0) {
                                  return 'Maximum fee must be greater than or equal to 0'
                                }
                                if (v && fields.transaction_fee_config.min_fee && v < fields.transaction_fee_config.min_fee) {
                                  return 'Maximum fee must be greater than or equal to minimum fee'
                                }
                                return true
                              },
                            ]"
                          />
                        </div>
                      </div>
                    </div>
                    <!-- Extra Fee -->
                    <div class="col-12">
                      <q-checkbox v-model="hasExtraFee" label="Add Extra Fee" @update:model-value="onExtraFeeToggle" />
                    </div>

                    <template v-if="hasExtraFee && fields.transaction_fee_config.extra_fee">
                      <div class="col-12 col-md-4">
                        <q-select
                          v-model="fields.transaction_fee_config.extra_fee.type"
                          emit-value
                          filled
                          map-options
                          label="Extra Fee Type"
                          :options="extraFeeTypeOptions"
                        />
                      </div>
                      <div class="col-12 col-md-4">
                        <q-input
                          v-model.number="fields.transaction_fee_config.extra_fee.value"
                          filled
                          step="any"
                          type="number"
                          :label="fields.transaction_fee_config.extra_fee.type === 'fixed' ? 'Amount' : 'Percentage'"
                        />
                      </div>
                    </template>
                  </template>
                </div>
              </q-card-section>

              <!-- errors -->
              <q-card-section v-if="fields.transaction_fee_config">
                <div class="text-negative">
                  <div v-if="errors.transaction_fee_config">
                    {{ errors.transaction_fee_config }}
                  </div>
                  <div v-else-if="errors.transaction_fee_config?.slabs">
                    <div v-for="(error, index) in errors.transaction_fee_config.slabs" :key="index">
                      {{ error }}
                    </div>
                  </div>
                </div>
                <div class="text-negative">
                  <div v-if="validationErrors.transaction_fee_config?.slabs">
                    <div v-for="(error, index) in validationErrors.transaction_fee_config.slabs" :key="index">
                      <div v-for="(message, key) in error" :key="key">
                        {{ key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) }}: {{ message }}
                      </div>
                    </div>
                  </div>
                  <div v-else-if="validationErrors.transaction_fee_config">
                    {{ validationErrors.transaction_fee_config }}
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn color="red" label="Cancel" @click="cancel" />
        <q-btn
          color="primary"
          label="Save"
          type="submit"
          :disable="loading || !!Object.keys(validationErrors).length || Object.keys(errors).length"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-form>
</template>
