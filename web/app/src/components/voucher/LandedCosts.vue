<script setup>
import FormattedNumber from 'src/components/FormattedNumber.vue'
import { useLandedCosts } from 'src/composables/useLandedCosts'
import { useLoginStore } from 'src/stores/login-info'
import { computed } from 'vue'

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

const fieldsValue = computed(() => props.fields)

const {
  showLandedCosts,
  landedCostTypes,
  AVAILABLE_CURRENCIES,
  addLandedCostRow,
  handleTypeChange,
  removeLandedCostRow,
  totalAdditionalCost,
  duty,
  taxBeforeDeclaration,
  declarationFees,
  totalOnDeclaration,
  totalTax,
  landedCostRows,
  averageRatePerItem,
} = useLandedCosts(fieldsValue)

// Handle tax scheme change for Tax on Purchase type
const handleTaxSchemeChange = (row) => {
  if (row.tax_scheme_id) {
    const taxScheme = props.formDefaults.collections?.tax_schemes?.results?.find(
      scheme => scheme.id === row.tax_scheme_id,
    )
    if (taxScheme) {
      if (row.type === 'Tax on Purchase') {
        row.value = taxScheme.rate
        row.is_percentage = true
        row.currency = loginStore.companyInfo.currency_code
      }
      row.tax_scheme = taxScheme
    }
  } else {
    row.tax_scheme = null
  }
}
</script>

<template>
  <q-card v-if="formDefaults.options?.enable_landed_costs">
    <q-card-section>
      <div class="row items-center q-mb-sm">
        <q-checkbox v-model="showLandedCosts" label="Additional Costs" />
      </div>
      <div v-if="showLandedCosts">
        <div v-if="landedCostRows.length" class="landed-costs-rows">
          <q-card v-for="(row, index) in landedCostRows" :key="index" class="landed-cost-row mb-4 px-4">
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
                          <q-select
                            v-if="!row.is_percentage && row.type !== 'Tax on Purchase'"
                            v-model="row.currency"
                            borderless
                            dense
                            emit-value
                            map-options
                            options-dense
                            style="min-width: 80px"
                            :options="AVAILABLE_CURRENCIES"
                          />
                          <span v-else>{{ row.is_percentage ? '%' : row.currency }}</span>
                        </template>
                      </q-input>
                    </div>
                    <div v-if="row.amount && row.is_percentage" class="text-grey-6 col-4 flex justify-end items-center">
                      <FormattedNumber
                        type="currency"
                        :currency="loginStore.companyInfo.currency_code"
                        :value="row.amount"
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

                <div class="col-12 col-md-5">
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

                <div class="col-1">
                  <q-btn
                    dense
                    flat
                    round
                    class="flex items-end justify-center"
                    color="negative"
                    icon="delete"
                    @click="removeLandedCostRow(index)"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
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
      </div>
    </q-card-section>

    <!-- Additional Costs Summary -->
    <q-card-section v-if="showLandedCosts" class="q-pa-md">
      <div class="text-h6 q-mb-sm">
        Additional Costs Summary
      </div>
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
            <span class="label">Total Additional:</span>
            <span class="value">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="totalAdditionalCost"
              />
            </span>
          </div>
        </div>
      </div>
    </q-card-section>
    <!-- Average Rate Summary -->

    <div v-if="showLandedCosts">
      <div class="text-h6 q-mb-md q-px-md">
        Average Rate Per Item
      </div>
      <q-table
        bordered
        flat
        hide-bottom
        :columns="[
          {
            name: 'item',
            label: 'Item Name',
            field: row => row.itemObj.name,
            align: 'left',
            style: 'width: 40%',
          },
          {
            name: 'base',
            label: 'Base Rate',
            field: 'rate',
            align: 'right',
            style: 'width: 20%',
            format: (val) => val,
          },
          {
            name: 'additional',
            label: 'Additional',
            field: 'additionalCost',
            align: 'right',
            style: 'width: 20%',
            format: (val) => val,
          },
          {
            name: 'total',
            label: 'Total',
            field: 'totalCost',
            align: 'right',
            style: 'width: 20%',
            format: (val) => val,
          },
        ]"
        :pagination="{ rowsPerPage: 0 }"
        :rows="averageRatePerItem"
        :rows-per-page-options="[0]"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td key="item" :props="props">
              {{ props.row.itemObj?.name || props.row.selected_item_obj?.name || props.row.item }}
            </q-td>
            <q-td key="base" :props="props">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="props.row.rate"
              />
            </q-td>
            <q-td key="additional" :props="props">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="props.row.additionalCost"
              />
            </q-td>
            <q-td key="total" :props="props">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="props.row.totalCost"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
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
