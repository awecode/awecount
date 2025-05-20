<script setup>
import FormattedNumber from 'src/components/FormattedNumber.vue'
import { useLandedCosts } from 'src/composables/useLandedCosts'
import { useLoginStore } from 'src/stores/login-info'
import { computed, watch } from 'vue'

const props = defineProps({
  fields: {
    type: Object,
    required: true,
  },
  formDefaults: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    required: false,
    default: () => ({}),
  },
})

const loginStore = useLoginStore()

// Create a computed property to ensure we're working with the reactive value
const fieldsValue = computed(() => props.fields)

// Calculate total amount from purchase voucher rows
const totalPurchaseAmount = computed(() => {
  if (!fieldsValue.value.rows) return 0
  return fieldsValue.value.rows.reduce((sum, row) => sum + (row.amount || 0), 0)
})

const {
  showLandedCosts,
  landedCostTypes,
  landedCostColumns,
  AVAILABLE_CURRENCIES,
  addLandedCostRow,
  handleTypeChange,
  removeLandedCostRow,
  averageRate,
  duty,
  taxBeforeDeclaration,
  declarationFees,
  totalOnDeclaration,
  totalTax,
  landedCostRows,
} = useLandedCosts(fieldsValue)

// Handle tax scheme change for Tax on Purchase type
const handleTaxSchemeChange = (row) => {
  if (row.type === 'Tax on Purchase' && row.tax_scheme_id) {
    const taxScheme = props.formDefaults.collections?.tax_schemes?.results?.find(
      scheme => scheme.id === row.tax_scheme_id,
    )
    if (taxScheme) {
      row.value = taxScheme.rate
      row.is_percentage = true
      row.currency = loginStore.companyInfo.currency_code
    }
  }
}
</script>

<template>
  <q-card v-if="formDefaults.options?.enable_landed_costs" class="q-mx-lg q-mt-md">
    <q-card-section :style="{ paddingLeft: '0px', paddingRight: '0px' }">
      <div class="row items-center q-mb-sm">
        <q-checkbox v-model="showLandedCosts" label="Landed Costs" />
      </div>
      <div v-if="showLandedCosts">
        <div class="row q-col-gutter-sm q-mb-sm">
          <div class="col-12">
            <q-btn
              color="primary"
              icon="add"
              label="Add Cost"
              size="sm"
              @click="addLandedCostRow"
            />
          </div>
        </div>
        <div v-if="landedCostRows.length" class="landed-costs-rows">
          <q-card v-for="(row, index) in landedCostRows" :key="index" class="landed-cost-row q-mb-sm">
            <q-card-section class="q-pa-sm">
              <div class="row q-col-gutter-sm">
                <!-- Type and Percentage -->
                <div class="col-12 col-md-6">
                  <div class="row q-col-gutter-sm">
                    <div class="col-8">
                      <q-select
                        v-model="row.type"
                        dense
                        emit-value
                        map-options
                        options-dense
                        label="Type"
                        :options="landedCostTypes"
                        @update:model-value="handleTypeChange(row)"
                      />
                    </div>
                    <div class="col-4">
                      <q-toggle
                        v-model="row.is_percentage"
                        class="full-width"
                        :disable="row.type === 'Tax on Purchase'"
                        :label="row.is_percentage ? 'Percentage' : 'Fixed'"
                      />
                    </div>
                  </div>
                </div>

                <!-- Amount and Currency -->
                <div class="col-12 col-md-6">
                  <div class="row q-col-gutter-sm">
                    <div class="col-8">
                      <q-input
                        v-model="row.value"
                        dense
                        label="Value"
                        type="number"
                        :error="!!errors?.landed_cost_rows?.[index]?.value"
                        :error-message="errors?.landed_cost_rows?.[index]?.value"
                        :readonly="row.type === 'Tax on Purchase'"
                      >
                        <template #append>
                          <span>{{ row.is_percentage ? '%' : row.currency }}</span>
                        </template>
                      </q-input>
                    </div>
                    <div class="col-4">
                      <q-select
                        v-model="row.currency"
                        dense
                        emit-value
                        map-options
                        options-dense
                        label="Currency"
                        :disable="row.is_percentage || row.type === 'Tax on Purchase'"
                        :options="AVAILABLE_CURRENCIES"
                      />
                    </div>
                  </div>
                </div>

                <!-- Tax Scheme and Credit Account -->
                <div class="col-12 col-md-6">
                  <n-auto-complete-v2
                    v-model="row.tax_scheme_id"
                    dense
                    emit-value
                    map-options
                    label="Tax Scheme"
                    option-label="name"
                    option-value="id"
                    :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/tax_schemes`"
                    :options="formDefaults.collections?.tax_schemes"
                    @update:model-value="handleTaxSchemeChange(row)"
                  >
                    <template #append>
                      <q-icon
                        v-if="row.tax_scheme_id"
                        class="cursor-pointer"
                        name="close"
                        @click.stop.prevent="row.tax_scheme_id = null"
                      />
                    </template>
                  </n-auto-complete-v2>
                </div>

                <div class="col-12 col-md-6">
                  <n-auto-complete-v2
                    v-if="row.type !== 'Customs Valuation Uplift'"
                    v-model="row.credit_account_id"
                    dense
                    emit-value
                    map-options
                    label="Credit Account"
                    option-label="name"
                    option-value="id"
                    :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/landed_cost_credit_accounts`"
                    :options="formDefaults.collections?.landed_cost_credit_accounts"
                  >
                    <template #append>
                      <q-icon
                        v-if="row.credit_account_id"
                        class="cursor-pointer"
                        name="close"
                        @click.stop.prevent="row.credit_account_id = null"
                      />
                    </template>
                  </n-auto-complete-v2>
                </div>

                <!-- Amount Display and Delete Button -->
                <div class="col-12">
                  <div class="row items-center justify-between">
                    <div class="col">
                      <div v-if="row.amount" class="text-grey-6 text-caption">
                        Amount: <FormattedNumber
                          type="currency"
                          :currency="loginStore.companyInfo.currency_code"
                          :value="row.amount"
                        />
                      </div>
                    </div>
                    <div class="col-auto">
                      <q-btn
                        dense
                        flat
                        round
                        color="negative"
                        icon="delete"
                        @click="removeLandedCostRow(index)"
                      />
                    </div>
                  </div>
                </div>
              </div>
              {{ row.amount }}
            </q-card-section>
          </q-card>

          <!-- Average Rate Summary -->
          <q-card class="q-mt-sm">
            <q-card-section class="q-pa-sm">
              <div class="row items-center justify-between">
                <div class="text-weight-medium">
                  Average rate per item:
                </div>
                <div class="text-weight-bold">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="averageRate"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>

    <!-- Declaration Summary -->
    <q-card-section class="q-pa-sm">
      <div class="text-h6 q-mb-sm">
        Declaration Summary
      </div>
      <q-card>
        <q-card-section class="q-pa-sm">
          <div class="row q-col-gutter-sm">
            <div class="col-12 col-md-6">
              <div class="declaration-summary-item">
                <span class="label">Duty:</span>
                <span class="value">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="duty"
                  />
                </span>
              </div>
              <div class="declaration-summary-item">
                <span class="label">Tax before declaration:</span>
                <span class="value">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="taxBeforeDeclaration"
                  />
                </span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <div class="declaration-summary-item">
                <span class="label">Declaration Fees (incl. tax):</span>
                <span class="value">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="declarationFees"
                  />
                </span>
              </div>
              <div class="declaration-summary-item">
                <span class="label">Total on Declaration:</span>
                <span class="value">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="totalOnDeclaration"
                  />
                </span>
              </div>
              <div class="declaration-summary-item">
                <span class="label">Total Tax:</span>
                <span class="value">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="totalTax"
                  />
                </span>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-card-section>
  </q-card>
</template>

<style scoped>
.landed-costs-rows {
  max-width: 1200px;
  margin: 0 auto;
}

.landed-cost-row {
  background-color: #f8f9fa;
}

.landed-cost-row .q-card-section {
  padding: 8px;
}

.declaration-summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}

.declaration-summary-item:last-child {
  border-bottom: none;
}

.declaration-summary-item .label {
  color: #666;
  font-weight: 500;
}

.declaration-summary-item .value {
  font-weight: 600;
}

@media (max-width: 1024px) {
  .landed-costs-rows {
    max-width: 100%;
  }
}
</style>
