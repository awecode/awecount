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

// Create a computed property to ensure we're working with the reactive value
const fieldsValue = computed(() => props.fields)

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
</script>

<template>
  <q-card v-if="formDefaults.options?.enable_landed_costs" class="q-mx-lg q-mt-md">
    <q-card-section :style="{ paddingLeft: '0px', paddingRight: '0px' }">
      <div class="row items-center q-mb-md">
        <q-checkbox v-model="showLandedCosts" label="Landed Costs" />
      </div>
      <div v-if="showLandedCosts">
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12">
            <q-btn
              color="primary"
              icon="add"
              label="Add Cost"
              @click="addLandedCostRow"
            />
          </div>
        </div>
        <q-table
          v-if="landedCostRows.length"
          bordered
          flat
          hide-pagination
          row-key="type"
          :columns="landedCostColumns"
          :rows="landedCostRows"
        >
          <template #body-cell-actions="cellProps">
            <q-td :props="cellProps">
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="removeLandedCostRow(cellProps.rowIndex)"
              />
            </q-td>
          </template>
          <template #body-cell-type="cellProps">
            <q-td :props="cellProps">
              <q-select
                v-model="cellProps.row.type"
                dense
                emit-value
                map-options
                options-dense
                :options="landedCostTypes"
                @update:model-value="handleTypeChange(cellProps.row)"
              />
            </q-td>
          </template>
          <template #body-cell-is_percentage="cellProps">
            <q-td :props="cellProps">
              <q-toggle
                v-model="cellProps.row.is_percentage"
                class="full-width"
                :label="cellProps.row.is_percentage ? 'Percentage' : 'Fixed'"
              />
            </q-td>
          </template>
          <template #body-cell-amount="cellProps">
            <q-td :props="cellProps">
              <div class="row items-center no-wrap">
                <q-input
                  v-model="cellProps.row.value"
                  dense
                  class="col"
                  type="number"
                  :error="!!errors?.landed_cost_rows?.[cellProps.rowIndex]?.value"
                  :error-message="errors?.landed_cost_rows?.[cellProps.rowIndex]?.value"
                  :value="cellProps.row.amount"
                />
                <span class="q-ml-sm text-no-wrap">{{ cellProps.row.is_percentage ? '%' : cellProps.row.currency }}</span>
                <div v-if="cellProps.row.amount" class="q-ml-sm text-grey-6 text-no-wrap">
                  (<FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="cellProps.row.amount"
                  />)
                </div>
              </div>
            </q-td>
          </template>
          <template #body-cell-currency="cellProps">
            <q-td :props="cellProps">
              <q-select
                v-model="cellProps.row.currency"
                dense
                emit-value
                map-options
                options-dense
                :disable="cellProps.row.is_percentage"
                :options="AVAILABLE_CURRENCIES"
              />
            </q-td>
          </template>
          <template #body-cell-tax_scheme="cellProps">
            <q-td :props="cellProps">
              <n-auto-complete-v2
                v-model="cellProps.row.tax_scheme_id"
                dense
                emit-value
                map-options
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/tax_schemes`"
                :options="formDefaults.collections?.tax_schemes"
              >
                <template #append>
                  <q-icon
                    v-if="cellProps.row.tax_scheme_id"
                    class="cursor-pointer"
                    name="close"
                    @click.stop.prevent="cellProps.row.tax_scheme_id = null"
                  />
                </template>
              </n-auto-complete-v2>
            </q-td>
          </template>
          <template #body-cell-credit_account="cellProps">
            <q-td :props="cellProps">
              <n-auto-complete-v2
                v-if="cellProps.row.type !== 'Customs Valuation Uplift'"
                v-model="cellProps.row.credit_account_id"
                dense
                emit-value
                map-options
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/landed_cost_credit_accounts`"
                :options="formDefaults.collections?.landed_cost_credit_accounts"
              >
                <template #append>
                  <q-icon
                    v-if="cellProps.row.credit_account_id"
                    class="cursor-pointer"
                    name="close"
                    @click.stop.prevent="cellProps.row.credit_account_id = null"
                  />
                </template>
              </n-auto-complete-v2>
            </q-td>
          </template>
          <template #bottom-row>
            <q-tr>
              <q-td class="text-right" colspan="6">
                Average rate per item:
              </q-td>
              <q-td class="text-left text-bold" colspan="2">
                <FormattedNumber
                  type="currency"
                  :currency="loginStore.companyInfo.currency_code"
                  :value="averageRate"
                />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </div>
    </q-card-section>
    <q-card-section>
      <div class="text-h6">
        Declaration Summary
      </div>
      <q-table
        bordered
        dense
        flat
        hide-bottom
        hide-header
        style="max-width: 400px"
        :columns="[
          { name: 'particular', label: 'Particular', field: 'particular', align: 'left' },
          { name: 'value', label: 'Value', field: 'value', align: 'right' },
        ]"
        :rows="[
          { particular: 'Duty', value: duty },
          { particular: 'Tax before declaration', value: taxBeforeDeclaration },
          { particular: 'Declaration Fees (incl. tax)', value: declarationFees },
          { particular: 'Total on Declaration', value: totalOnDeclaration },
          { particular: 'Total Tax', value: totalTax },
        ]"
      >
        <template #body-cell-value="cellProps">
          <q-td :props="cellProps">
            <FormattedNumber
              type="currency"
              :currency="loginStore.companyInfo.currency_code"
              :value="cellProps.row.value"
            />
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>
</template>
