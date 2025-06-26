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
const roundUp = computed(() => props.formDefaults.options?.round_up_additional_costs)

const {
  showLandedCosts,
  LANDED_COST_TYPES,
  AVAILABLE_CURRENCIES,
  addLandedCostRow,
  handleTypeChange,
  removeLandedCostRow,
  updateLandedCostRow,
  totalAdditionalCost,
  taxOnDeclaration,
  duty,
  taxBeforeDeclaration,
  declarationFees,
  totalOnDeclaration,
  totalTax,
  averageRatePerItem,
} = useLandedCosts(fieldsValue, {
  roundUp,
})

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
        <q-checkbox v-model="showLandedCosts" label="Additional Costs" :disable="!!fields.landed_cost_rows?.length && showLandedCosts" />
      </div>
      <div v-if="showLandedCosts">
        <div v-if="fields.landed_cost_rows?.length">
          <q-table
            bordered
            dense
            flat
            hide-bottom
            :columns="[
              {
                name: 'type',
                label: 'Type',
                field: 'type',
                align: 'left',
                style: 'width: 22%; min-width: 200px',
              },
              {
                name: 'value',
                label: 'Value',
                field: 'value',
                align: 'right',
                style: 'width: 15%; min-width: 120px',
              },
              {
                name: 'currency',
                label: 'Currency',
                field: 'currency',
                align: 'center',
                style: 'width: 10%; min-width: 100px',
              },
              {
                name: 'tax_scheme',
                label: 'Tax Scheme',
                field: 'tax_scheme_id',
                align: 'left',
                style: 'width: 20%; min-width: 180px',
              },
              {
                name: 'credit_account',
                label: 'Credit Account',
                field: 'credit_account_id',
                align: 'left',
                style: 'width: 25%; min-width: 200px',
              },
              {
                name: 'amount',
                label: 'Amount',
                field: 'amount',
                align: 'right',
                style: 'width: 8%; min-width: 80px',
              },
              {
                name: 'actions',
                label: '',
                field: 'actions',
                align: 'center',
                style: 'width: 10%; min-width: 80px',
              },
            ]"
            :pagination="{ rowsPerPage: 0 }"
            :rows="fields.landed_cost_rows"
            :rows-per-page-options="[0]"
          >
            <template #body="slotProps">
              <q-tr class="cursor-pointer" :class="slotProps.rowIndex % 2 === 1 ? 'bg-grey-2' : ''" :props="slotProps">
                <q-td key="type" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <div class="flex items-center q-gutter-xs full-width" style="min-height: 32px;">
                    <div style="flex: 1">
                      <q-select
                        v-model="slotProps.row.type"
                        dense
                        emit-value
                        map-options
                        options-dense
                        :error="!!errors?.landed_cost_rows?.[slotProps.rowIndex]?.type?.[0]"
                        :error-message="errors?.landed_cost_rows?.[slotProps.rowIndex]?.type?.[0]"
                        :options="LANDED_COST_TYPES"
                        @update:model-value="() => {
                          handleTypeChange(slotProps.row)
                          updateLandedCostRow(slotProps.rowIndex)
                        }"
                      />
                    </div>
                    <div>
                      <q-toggle
                        v-model="slotProps.row.is_percentage"
                        dense
                        class="text-caption"
                        size="xs"
                        :disable="slotProps.row.type === 'Tax on Purchase'"
                        :error="!!errors?.landed_cost_rows?.[slotProps.rowIndex]?.is_percentage?.[0]"
                        :error-message="errors?.landed_cost_rows?.[slotProps.rowIndex]?.is_percentage?.[0]"
                        :label="slotProps.row.is_percentage ? '%' : 'Fixed'"
                        @update:model-value="updateLandedCostRow(slotProps.rowIndex)"
                      />
                    </div>
                  </div>
                </q-td>
                <q-td key="value" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <q-input
                    v-model="slotProps.row.value"
                    dense
                    class="q-ma-none"
                    type="number"
                    :error="!!errors?.landed_cost_rows?.[slotProps.rowIndex]?.value?.[0]"
                    :error-message="errors?.landed_cost_rows?.[slotProps.rowIndex]?.value?.[0]"
                    :readonly="slotProps.row.type === 'Tax on Purchase'"
                    @update:model-value="updateLandedCostRow(slotProps.rowIndex)"
                  />
                </q-td>
                <q-td key="currency" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <div v-if="!slotProps.row.is_percentage && slotProps.row.type !== 'Tax on Purchase'">
                    <q-select
                      v-model="slotProps.row.currency"
                      dense
                      emit-value
                      map-options
                      options-dense
                      class="q-ma-none"
                      :error="!!errors?.landed_cost_rows?.[slotProps.rowIndex]?.currency?.[0]"
                      :error-message="errors?.landed_cost_rows?.[slotProps.rowIndex]?.currency?.[0]"
                      :options="AVAILABLE_CURRENCIES"
                      @update:model-value="updateLandedCostRow(slotProps.rowIndex)"
                    />
                  </div>
                  <div v-else class="text-center">
                    <q-chip
                      dense
                      class="q-ma-none text-body2"
                      color="grey-4"
                      text-color="grey-8"
                    >
                      {{ slotProps.row.is_percentage ? '%' : slotProps.row.currency }}
                    </q-chip>
                  </div>
                </q-td>
                <q-td key="tax_scheme" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <n-auto-complete-v2
                    v-model="slotProps.row.tax_scheme_id"
                    borderless
                    dense
                    emit-value
                    map-options
                    class="q-ma-none"
                    option-label="name"
                    option-value="id"
                    :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/tax_schemes/`"
                    :error="errors?.landed_cost_rows?.[slotProps.rowIndex]?.tax_scheme_id?.[0]"
                    :options="formDefaults.collections?.tax_schemes"
                    @update:model-value="handleTaxSchemeChange(slotProps.row)"
                  >
                    <template #append>
                      <q-icon
                        v-if="slotProps.row.tax_scheme_id"
                        class="cursor-pointer"
                        name="close"
                        size="xs"
                        @click.stop.prevent="slotProps.row.tax_scheme_id = null"
                      />
                    </template>
                  </n-auto-complete-v2>
                </q-td>
                <q-td key="credit_account" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <n-auto-complete-v2
                    v-if="!(slotProps.row.type === 'Customs Valuation Uplift' && (!slotProps.row.tax_scheme_id || !parseFloat(slotProps.row.tax_scheme?.rate)))"
                    v-model="slotProps.row.credit_account_id"
                    borderless
                    dense
                    emit-value
                    map-options
                    class="q-ma-none"
                    option-label="name"
                    option-value="id"
                    :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/landed_cost_credit_accounts/`"
                    :error="errors?.landed_cost_rows?.[slotProps.rowIndex]?.credit_account_id?.[0]"
                    :label="`${slotProps.row.type === 'Customs Valuation Uplift' ? 'Credit Account for Tax' : 'Credit Account'}`"
                    :options="formDefaults.collections?.landed_cost_credit_accounts"
                  >
                    <template #append>
                      <q-icon
                        v-if="slotProps.row.credit_account_id"
                        class="cursor-pointer"
                        name="close"
                        size="xs"
                        @click.stop.prevent="slotProps.row.credit_account_id = null"
                      />
                    </template>
                  </n-auto-complete-v2>
                </q-td>
                <q-td key="amount" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="slotProps.row.amount"
                  />
                </q-td>
                <q-td key="actions" class="q-pa-xs bg-grey-1 text-center" :props="slotProps">
                  <q-btn
                    dense
                    flat
                    round
                    class="q-ma-none"
                    color="negative"
                    icon="delete"
                    size="sm"
                    @click="removeLandedCostRow(slotProps.rowIndex)"
                  />
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </div>
        <div class="row q-col-gutter-sm q-mt-sm">
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
      <div class="text-h6 q-mb-md">
        Additional Costs Summary
      </div>
      <div class="summary-grid">
        <div class="summary-item">
          <span class="label">Duty:</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="duty"
            />
          </span>
        </div>
        <div class="summary-item">
          <span class="label">Declaration Fees (incl. tax):</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="declarationFees"
            />
          </span>
        </div>
        <div class="summary-item">
          <span class="label">Tax before declaration:</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="taxBeforeDeclaration"
            />
          </span>
        </div>
        <div class="summary-item total-item">
          <span class="label">Total on Declaration:</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="totalOnDeclaration"
            />
          </span>
        </div>
        <div class="summary-item">
          <span class="label">Tax on Declaration:</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="taxOnDeclaration"
            />
          </span>
        </div>
        <div class="summary-item total-item">
          <span class="label">Total Tax:</span>
          <span class="value">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="totalTax"
            />
          </span>
        </div>
        <div class="summary-item total-item">
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
        <template #body="slotProps">
          <q-tr :props="slotProps">
            <q-td key="item" class="q-pa-sm" :props="slotProps">
              {{ slotProps.row.itemObj?.name || slotProps.row.selected_item_obj?.name || slotProps.row.item }}
            </q-td>
            <q-td key="base" class="q-pa-sm text-right" :props="slotProps">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="slotProps.row.rate || 0"
              />
            </q-td>
            <q-td key="additional" class="q-pa-sm text-right" :props="slotProps">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="slotProps.row.additionalCost"
              />
            </q-td>
            <q-td key="total" class="q-pa-sm text-right" :props="slotProps">
              <FormattedNumber
                type="currency"
                :currency="loginStore.companyInfo.currency_code"
                :value="slotProps.row.totalCost"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  </q-card>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-top: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.summary-item .label {
  font-weight: 500;
}

.summary-item .value {
  font-weight: 600;
}

.total-item {
  background-color: #e3f2fd;
  border-color: #2196f3;
}

@media (min-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

/* Table border styling */
.q-table--bordered {
  border: 1px solid #e0e0e0 !important;
}

.q-table--bordered th {
  border-right: 1px solid #e0e0e0 !important;
  border-bottom: 1px solid #e0e0e0 !important;
}

.q-table--bordered th:last-child {
  border-right: none !important;
}

.q-table--bordered td {
  border-right: 1px solid #e0e0e0 !important;
  border-bottom: 1px solid #e0e0e0 !important;
}

.q-table--bordered td:last-child {
  border-right: none !important;
}

.q-table--bordered tr:last-child td {
  border-bottom: none !important;
}
</style>
