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
              :error="!!errors.name"
              :error-message="errors.name"
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
              :error="!!errors.account"
              :error-message="errors.account"
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
                        endpoint="v1/payment-modes/create-defaults/accounts"
                        option-value="id"
                        option-label="name"
                        :rules="[v => !fields.transaction_fee_config || !!v || 'Fee account is required when fee is enabled']"
                        filled
                        :error="!!errors.transaction_fee_account"
                        :error-message="errors.transaction_fee_account"
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
                          min="0"
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
                          min="0"
                          :rules="[
                            v => v > 0 || 'Percentage must be greater than 0',
                            v => v <= 100 || 'Percentage must be less than or equal to 100'
                          ]"
                        />
                      </div>
                    </template>

                    <!-- Slab Based Fee -->
                    <template v-if="fields.transaction_fee_config.type === 'slab_based' || fields.transaction_fee_config.type === 'sliding_scale'">
                      <div class="col-12">
                        <div class="text-subtitle2 q-mb-sm">{{ fields.transaction_fee_config.type === 'slab_based' ? 'Fee Slabs' : 'Sliding Scale Slabs' }}</div>
                        <div v-for="(slab, index) in fields.transaction_fee_config.slabs" :key="index" class="row q-col-gutter-sm q-mb-md">
                          <div class="col-12 col-md-3">
                            <q-input
                              v-model.number="slab.min_amount"
                              label="Min Amount"
                              type="number"
                              step="any"
                              filled
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.min_amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.min_amount"
                              min="0"
                              :rules="[v => v >= 0 || 'Minimum amount must be greater than or equal to 0']"
                            />
                          </div>
                          <div class="col-12 col-md-3" v-if="fields.transaction_fee_config.type === 'slab_based'">
                            <q-input
                              v-model.number="slab.max_amount"
                              label="Max Amount"
                              type="number"
                              step="any"
                              filled
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.max_amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.max_amount"
                              min="0"
                              :rules="[v => v >= 0 || 'Maximum amount must be greater than or equal to 0']"
                            />
                          </div>
                          <div class="col-12 col-md-3">
                            <q-select
                              v-model="slab.fee_type"
                              :options="slabFeeTypeOptions"
                              label="Fee Type"
                              filled
                              emit-value
                              map-options
                              @update:model-value="onSlabFeeTypeChange(index)"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.fee_type"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.fee_type"
                            />
                          </div>
                          <div class="col-12 col-md-2">
                            <q-input
                              v-model.number="slab.rate"
                              v-if="slab.fee_type === 'rate'"
                              label="Rate (%)"
                              type="number"
                              step="any"
                              filled
                              min="0"
                              :rules="[v => v >= 0 || 'Rate must be greater than or equal to 0', v => v <= 100 || 'Rate must be less than or equal to 100']"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.rate"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.rate"
                            />
                            <q-input
                              v-else
                              v-model.number="slab.amount"
                              label="Fixed Amount"
                              type="number"
                              step="any"
                              filled
                              min="0"
                              :rules="[v => v >= 0 || 'Amount must be greater than or equal to 0']"
                              :error="!!validationErrors.transaction_fee_config?.slabs?.[index]?.amount"
                              :error-message="validationErrors.transaction_fee_config?.slabs?.[index]?.amount"
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
                          color="primary"
                          :label="`Add ${fields.transaction_fee_config.type === 'slab_based' ? 'Slab' : 'Scale'}`"
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
                          min="0"
                          :rules="[v => {
                            if (v && v < 0) {
                              return 'Minimum fee must be greater than or equal to 0'
                            }
                            if (v && fields.transaction_fee_config.max_fee && v > fields.transaction_fee_config.max_fee) {
                              return 'Minimum fee must be less than or equal to maximum fee'
                            }
                            return true
                          }]"
                        />
                      </div>
                      <div class="col-12 col-md-6">
                      <q-input
                        v-model.number="fields.transaction_fee_config.max_fee"
                        label="Maximum Fee"
                        type="number"
                        step="any"
                        filled
                        min="0"
                        :rules="[v => {
                          if (v && v < 0) {
                            return 'Maximum fee must be greater than or equal to 0'
                          }
                          if (v && fields.transaction_fee_config.min_fee && v < fields.transaction_fee_config.min_fee) {
                            return 'Maximum fee must be greater than or equal to minimum fee'
                          }
                          return true
                        }]"
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
                          emit-value
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
                          {{ key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }}: {{ message }}
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
          :disable="loading || !!Object.keys(validationErrors).length || Object.keys(errors).length"
        />
      </q-card-actions>
    </q-card>
  </q-form>
</template>

<script setup>
import { ref, computed } from 'vue'

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
        sliding_scale: validateSlidingScale
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
      if (('rate' in slab) === ('amount' in slab)) {
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

      if (('rate' in slab) === ('amount' in slab)) {
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
    validateFeeConfig
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

watch(() => fields.value.transaction_fee_config, (value) => {
  hasTransactionFee.value = !!value

  if (value) {
    hasExtraFee.value = !!value.extra_fee
    
    validateFeeConfig(value)
    if(value.min_fee === '') {
      delete fields.value.transaction_fee_config.min_fee
    }
    if(value.max_fee === '') {
      delete fields.value.transaction_fee_config.max_fee
    }
  }
}, {
  immediate: true ,
  deep: true
})




const onTransactionFeeToggle = (value) => {
  if (!!fields.value.transaction_fee_config) {
    return
  }

  if (value) {
    fields.value.transaction_fee_config = {
      type: 'fixed',
      value: 0,
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

const slabFeeTypeOptions = [
  { label: 'Rate (%)', value: 'rate' },
  { label: 'Fixed Amount', value: 'amount' }
]

const onFeeTypeChange = (type) => {
  if (type.value === null) {
    fields.value.transaction_fee_config = null
    return
  }

  fields.value.transaction_fee_config = {
    type: type.value,
    ...(type.value === 'slab_based' || type.value === 'sliding_scale' ? { slabs: [] } : { value: 0 })
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
      value: 0
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
    rate: 0
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
