<script setup lang="ts">
import Decimal from 'decimal.js'
import FormattedNumber from 'src/components/FormattedNumber.vue'
import checkPermissions from 'src/composables/checkPermissions'
import ItemForm from 'src/pages/inventory/item/ItemForm.vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

interface Props {
  itemOptions?: {
    results: any[]
    pagination: Record<string, any>
  }
  unitOptions?: {
    results: any[]
    pagination: Record<string, any>
  }
  discountOptions?: any[]
  errors?: Record<string, string[]> | null
  rowEmpty?: boolean
  usedIn?: 'sales' | 'purchase' | 'creditNote' | null
  usedInPos?: boolean
  taxOptions?: {
    results: any[]
    pagination: Record<string, any>
  }
  taxType?: string | null
  modelValue?: {
    quantity: number
    rate: number | string
    item_id: number | null
    unit_id: number | null
    description: string
    discount: number
    discount_type: string | null
    itemObj: any | null
    tax_scheme_id: string | null
    discount_id: number | null
    trade_discount: boolean
    is_returned?: boolean
    selected_unit_obj?: any
    selected_tax_scheme_obj?: any
    selected_item_obj?: any
    name?: string
    discountObj?: any | null
    missingFields?: string[] | null
  }
  index?: number | null
  enableRowDescription?: boolean
  showRowTradeDiscount?: boolean
  inputAmount?: boolean
  showRateQuantity?: boolean
  isFifo?: boolean
  cogsData?: Record<string, any> | null
  hasChallan?: boolean
  missingFieldsConfig?: {
    enabled: boolean
    fields: Record<string, boolean>
  }
}

const props = withDefaults(defineProps<Props>(), {
  itemOptions: () => ({ results: [], pagination: {} }),
  unitOptions: () => ({ results: [], pagination: {} }),
  discountOptions: () => [],
  errors: null,
  rowEmpty: false,
  usedIn: null,
  usedInPos: false,
  taxOptions: () => ({ results: [], pagination: {} }),
  taxType: null,
  modelValue: () => ({
    quantity: 1,
    rate: '',
    item_id: null,
    unit_id: null,
    description: '',
    discount: 0,
    discount_type: null,
    itemObj: null,
    tax_scheme_id: '',
    discount_id: null,
    trade_discount: false,
    discountObj: null,
    missingFields: null,
  }),
  index: null,
  enableRowDescription: false,
  showRowTradeDiscount: false,
  inputAmount: false,
  showRateQuantity: true,
  isFifo: false,
  cogsData: null,
  hasChallan: false,
  missingFieldsConfig: () => ({
    enabled: false,
    fields: {},
  }),
})

const emit = defineEmits<{
  'update:modelValue': [value: Props['modelValue']]
  'deleteRow': [index: number]
  'onItemIdUpdate': [value?: number]
}>()

const route = useRoute()
const expandedState = ref(false)
const modalValue = ref(props.modelValue)
const amountComputed = computed(() => new Decimal(modalValue.value.rate || 0).mul(modalValue.value.quantity || 0).toNumber())
const oldTaxSchemeId = ref<string | null>(null)

watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
    emit('update:modelValue', newValue)
  },
)

watch(
  () => modalValue.value,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { deep: true },
)

watch(
  () => props.taxType,
  (newTaxType) => {
    if (newTaxType === 'no_tax') {
      oldTaxSchemeId.value = modalValue.value.tax_scheme_id
      modalValue.value.tax_scheme_id = null
    } else if (oldTaxSchemeId.value) {
      modalValue.value.tax_scheme_id = oldTaxSchemeId.value
      oldTaxSchemeId.value = null
    }
  },
  { deep: true },
)

watch(
  () => props.errors,
  (newValue) => {
    if (newValue?.tax_scheme_id || newValue?.unit_id) {
      expandedState.value = true
    }
  },
)

watch(
  () => props.modelValue.discount_type,
  (newValue) => {
    if (typeof newValue === 'number') {
      const index = props.discountOptions.findIndex(item => newValue === item.id)
      modalValue.value.discountObj = props.discountOptions[index]
    } else if (newValue === null) {
      modalValue.value.discountObj = null
      modalValue.value.discount = null
    } else {
      modalValue.value.discountObj = null
    }
  },
)

const deleteRow = (index: number) => {
  emit('deleteRow', index)
}

onMounted(() => {
  if (props.usedIn === 'creditNote') modalValue.value.is_returned = true
})

const onAmountInput = (amount: number) => {
  const currentAmount = new Decimal(modalValue.value.rate || 0).mul(modalValue.value.quantity || 1)
  const newAmount = new Decimal(amount)

  if (!newAmount.equals(currentAmount)) {
    if (!modalValue.value.quantity) {
      modalValue.value.quantity = 1
    }
    modalValue.value.rate = newAmount.div(modalValue.value.quantity).toNumber()
  }
}

if (props.isFifo && props.usedIn === 'sales' && !route.params.id && !props.usedInPos) {
  watch(
    () => modalValue.value.item_id,
    (newValue) => {
      if (modalValue.value.item_id) {
        emit('onItemIdUpdate', newValue)
      }
    },
  )
  watch(
    () => modalValue.value.quantity,
    () => {
      if (modalValue.value.item_id) {
        emit('onItemIdUpdate')
      }
    },
  )
}

const updateItem = (itemObject: any) => {
  if (itemObject) {
    modalValue.value.itemObj = itemObject
    modalValue.value.item_id = itemObject.id
    modalValue.value.description = itemObject.description
    modalValue.value.rate = itemObject.rate
    modalValue.value.unit_id = itemObject.unit_id
    modalValue.value.tax_scheme_id = props.taxType === 'no_tax' ? null : itemObject.tax_scheme_id
    modalValue.value.selected_unit_obj = itemObject.default_unit_obj
    modalValue.value.selected_tax_scheme_obj = itemObject.default_tax_scheme_obj

    // Check for missing fields based on config
    if (props.missingFieldsConfig?.enabled) {
      const missingFields = []
      const fieldLabels: Record<string, string> = {
        code: 'Code',
        hs_code: 'HS Code',
      }

      Object.entries(props.missingFieldsConfig.fields).forEach(([field, enabled]) => {
        if (enabled && (!itemObject[field] || itemObject[field].trim() === '')) {
          missingFields.push(fieldLabels[field] || field)
        }
      })

      if (missingFields.length > 0) {
        modalValue.value.missingFields = missingFields
      } else {
        modalValue.value.missingFields = null
      }
    } else {
      modalValue.value.missingFields = null
    }
  }
}

const choiceEndpointBaseComputed = computed(() => {
  if (props.usedIn === 'sales') return 'sales-voucher'
  if (props.usedIn === 'purchase') return 'purchase-vouchers'
  if (props.usedIn === 'creditNote') return 'credit-note'
  return ''
})
</script>

<template>
  <div :class="usedInPos ? '-mt-12' : ''">
    <div class="row q-col-gutter-md no-wrap">
      <div class="col-5 row">
        <div data-testid="item" :class="usedIn === 'creditNote' ? 'col-10' : 'col-12'">
          <n-auto-complete-v2
            v-if="!usedInPos"
            v-model="modalValue.item_id"
            label="Item"
            :disabled="usedInPos || hasChallan"
            :emit-obj="true"
            :endpoint="`/api/company/${$route.params.company}/${choiceEndpointBaseComputed}/create-defaults/items`"
            :error="
              errors?.item_id ? errors?.item_id[0]
              : rowEmpty ? 'Item is required'
                : ''
            "
            :modal-component="
              usedInPos || hasChallan ? undefined
              : checkPermissions('inventoryaccount.create') ? ItemForm
                : undefined
            "
            :options="itemOptions"
            :static-option="modelValue.selected_item_obj"
            @update-obj="updateItem"
          />
          <q-input
            v-else
            disable
            :label="usedInPos ? '' : 'Item'"
            :model-value="modelValue.name"
          />
        </div>
        <div v-if="modalValue.missingFields" class="text-orange text-sm -mt-2">
          Item is missing required fields: {{ modalValue.missingFields.join(', ') }}
        </div>
        <div v-if="usedIn === 'creditNote'" class="col-2 row justify-center">
          <q-checkbox v-model="modalValue.is_returned" :false-value="null" />
        </div>
      </div>
      <div class="col-2">
        <span v-if="showRateQuantity" data-testid="quantity-input">
          <q-input
            v-model.number="modalValue.quantity"
            type="number"
            :disable="hasChallan"
            :error="errors?.quantity ? true : false"
            :error-message="errors?.quantity ? errors.quantity[0] : null"
            :label="usedInPos ? '' : 'Quantity'"
          >
            <template v-if="isFifo && Object.hasOwn(cogsData, index)" #append>
              <q-icon v-if="cogsData[index].totalCost.status === 'error'" color="orange" name="mdi-alert">
                <q-tooltip>
                  {{ cogsData[index].totalCost.message }}
                  <br />
                  Available Quantity {{ cogsData[index].availableStock }}
                </q-tooltip>
              </q-icon>
              <span v-else class="text-sm mt-4 text-blue-400">
                <q-tooltip>Available Stock</q-tooltip>
                {{ cogsData[index].availableStock }}
              </span>
            </template>
          </q-input>
        </span>
      </div>
      <div class="col-2">
        <div v-if="showRateQuantity" data-testid="rate-input">
          <q-input
            v-model.number="modalValue.rate"
            type="number"
            :error="errors?.rate ? true : false"
            :error-message="errors?.rate ? errors.rate[0] : null"
            :label="usedInPos ? '' : 'Rate'"
          >
            <template v-if="isFifo && Object.hasOwn(cogsData, index)" #append>
              <span v-if="cogsData[index].totalCost.status !== 'error'" class="text-sm mt-4 text-blue-400">
                <q-tooltip>Cost Rate as per Fifo.</q-tooltip>
                <FormattedNumber type="currency" :value="new Decimal(cogsData[index].totalCost).div(modalValue.quantity).toNumber()" />
              </span>
            </template>
          </q-input>
        </div>
      </div>
      <div v-if="inputAmount" class="col-2" data-testid="amount-input">
        <q-input v-model="amountComputed" label="Amount" @change="onAmountInput">
          <template v-if="isFifo && Object.hasOwn(cogsData, index) && cogsData[index].totalCost.status !== 'error'" #append>
            <span class="text-sm mt-4 text-blue-400">
              <q-tooltip>Total Cost Price as per Fifo.</q-tooltip>
              <FormattedNumber type="currency" :value="cogsData[index].totalCost" />
            </span>
          </template>
        </q-input>
      </div>
      <div v-else class="col-2 row justify-center items-center" data-testid="amount-input">
        <span class="">
          <FormattedNumber type="currency" :value="amountComputed" />
          <span v-if="isFifo && Object.hasOwn(cogsData, index) && cogsData[index].totalCost.status !== 'error'" class="relative bg-red-200">
            <span class="text-sm ml-2 text-blue-400 absolute top-1/2 -right-0 -translate-y-1/2">
              <q-tooltip>Total Cost Price as per Fifo.</q-tooltip>
              <FormattedNumber type="currency" :value="cogsData[index].totalCost" />
            </span>
          </span>
        </span>
      </div>
      <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
        <q-btn
          flat
          class="q-pa-sm focus-highLight"
          color="transparent"
          data-testid="expand-btn"
          @click="() => (expandedState = !expandedState)"
        >
          <q-icon
            class="cursor-pointer"
            color="green"
            name="mdi-arrow-expand"
            size="20px"
          >
            <q-tooltip>Expand</q-tooltip>
          </q-icon>
        </q-btn>
        <q-btn
          flat
          class="q-pa-sm focus-highLight"
          color="transparent"
          data-testid="row-delete-btn"
          :disable="hasChallan"
          @click="() => deleteRow(index)"
        >
          <q-icon
            class="cursor-pointer"
            color="negative"
            name="delete"
            size="20px"
          />
        </q-btn>
      </div>
    </div>
    <div v-if="expandedState">
      <div class="row q-col-gutter-md q-px-lg">
        <div class="col-grow" data-testid="unit-select">
          <n-auto-complete-v2
            v-model="modalValue.unit_id"
            label="Unit"
            :emit-obj="usedInPos"
            :endpoint="`/api/company/${$route.params.company}/${choiceEndpointBaseComputed}/create-defaults/units`"
            :error="errors?.unit_id ? errors?.unit_id[0] : ''"
            :options="unitOptions"
            :static-option="modalValue.selected_unit_obj"
            @update-obj="(val) => (modalValue.selected_unit_obj = val)"
          />
        </div>
        <div class="col-5">
          <div class="row q-col-gutter-md">
            <div data-testid="row-discount-type-div" :class="['Amount', 'Percent'].includes(modalValue.discount_type) ? 'col-5' : 'col-12'">
              <n-auto-complete v-model="modalValue.discount_type" label="Discount" :options="discountOptions" />
            </div>
            <div v-if="modalValue.discount_type === 'Amount' || modalValue.discount_type === 'Percent'" :class="showRowTradeDiscount ? 'col-3' : 'col-6'">
              <q-input
                v-model.number="modalValue.discount"
                data-testid="row-discount-input"
                label="Discount"
                :error="errors?.discount ? true : false"
                :error-message="errors?.discount ? errors.discount[0] : null"
              />
            </div>
            <div v-if="['Amount', 'Percent'].includes(modalValue.discount_type) && showRowTradeDiscount" class="col-3 row">
              <q-checkbox v-model="modalValue.trade_discount" data-testid="row-trade-discount-checkbox" label="Trade Discount?" />
            </div>
          </div>
        </div>
        <div v-if="taxType !== 'no_tax'" class="col-3" data-testid="row-tax-select">
          <n-auto-complete-v2
            v-model="modalValue.tax_scheme_id"
            label="Tax"
            :emit-obj="true"
            :endpoint="`/api/company/${$route.params.company}/${choiceEndpointBaseComputed}/create-defaults/tax_schemes`"
            :error="errors?.tax_scheme_id ? 'This field is required' : ''"
            :options="props.taxOptions"
            :static-option="modalValue.selected_tax_scheme_obj"
            @update-obj="(val) => (modalValue.selected_tax_scheme_obj = val)"
          />
        </div>
      </div>
      <div v-if="$route.params.id ? (!!modalValue.item_id || !!modalValue.itemObj) && enableRowDescription : !!modalValue.itemObj && enableRowDescription">
        <q-input
          v-model="modalValue.description"
          class="q-mb-lg"
          data-testid="row-description-input"
          label="Description"
          type="textarea"
        />
      </div>
    </div>
  </div>
</template>
