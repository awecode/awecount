<script setup lang="ts">
import Decimal from 'decimal.js'
import FormattedNumber from 'src/components/FormattedNumber.vue'
import useApi from 'src/composables/useApi'
import useCalcDiscount from 'src/composables/useCalcDiscount.js'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import InvoiceRow from './InvoiceRow.vue'

interface RowData {
  discount: number
  quantity: number
  rate: number | string
  item_id: number | null
  unit_id: number | null
  description: string
  discount_type: string | null
  tax_scheme_id: string | null
  discount_id: number | null
  trade_discount: boolean
  id?: number
  itemObj: any
  discountObj?: any
}

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
  taxOptions?: {
    results: any[]
    pagination: Record<string, any>
  }
  taxType?: string | null
  mainDiscount?: {
    discount_type: string | null
    discount: number
  }
  errors?: any[] | string | null
  usedIn?: 'sales' | 'purchase' | 'creditNote' | null
  modelValue?: RowData[]
  enableRowDescription?: boolean
  showRowTradeDiscount?: boolean
  inputAmount?: boolean
  showRateQuantity?: boolean
  isFifo?: boolean
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
  taxOptions: () => ({ results: [], pagination: {} }),
  taxType: null,
  mainDiscount: () => ({ discount_type: null, discount: 0 }),
  errors: null,
  usedIn: null,
  modelValue: () => [{
    discount: 0,
    quantity: 1,
    rate: '',
    item_id: null,
    unit_id: null,
    description: '',
    discount_type: null,
    tax_scheme_id: null,
    discount_id: null,
    trade_discount: false,
    itemObj: null,
  }],
  enableRowDescription: false,
  showRowTradeDiscount: false,
  inputAmount: false,
  showRateQuantity: true,
  isFifo: false,
  hasChallan: false,
  missingFieldsConfig: () => ({
    enabled: false,
    fields: {},
  }),
})

const emit = defineEmits<{
  'update:modelValue': [value: RowData[]]
  'deleteRowErr': [index: number, row: RowData | null]
  'updateVoucherMeta': [value: any]
}>()

const route = useRoute()
const defaultRowData: RowData = {
  quantity: 1,
  rate: '',
  item_id: null,
  unit_id: null,
  description: '',
  discount: 0,
  discount_type: null,
  tax_scheme_id: null,
  discount_id: null,
  trade_discount: false,
  itemObj: null,
}
const modalValue = ref<RowData[]>(props.modelValue || [defaultRowData])
const rowEmpty = ref(false)
const itemPurchaseData = ref<Record<number, any>>({})
const COGSData = ref<Record<number, { totalCost: number | { status: string, message: string }, availableStock: number }> | null>(null)

watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
  },
)

watch(
  () => props.errors,
  (newValue) => {
    if (newValue === 'This field is required.') {
      rowEmpty.value = true
    } else {
      rowEmpty.value = false
    }
  },
)

watch(
  () => modalValue.value,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { deep: true },
)

const taxOptions = computed(() => {
  if (Array.isArray(props.taxOptions)) {
    return props.taxOptions
  }
  return props.taxOptions?.results || []
})

const totalDataComputed = computed(() => {
  const data = {
    subTotal: new Decimal(0),
    discount: new Decimal(0),
    total: new Decimal(0),
    totalTax: new Decimal(0),
    sameScheme: null as number | null,
    taxObj: null as any,
    taxName: null as string | null,
    taxRate: null as number | null,
    taxableAmount: new Decimal(0),
    addTotal: new Decimal(0),
  }

  modalValue.value.forEach((item) => {
    data.addTotal = data.addTotal.add(new Decimal(item.rate || 0).mul(item.quantity || 0))
  })

  modalValue.value.forEach((item, index) => {
    let currentTaxObj = null

    if (item.tax_scheme_id && taxOptions.value.length && props.taxType !== 'No Tax') {
      const taxIndex = taxOptions.value.findIndex(taxItem => taxItem.id === item.tax_scheme_id)
      if (taxIndex > -1) {
        currentTaxObj = taxOptions.value[taxIndex]
      }
    }

    let updatedRate = new Decimal(item.rate || 0)
    if (props.taxType === 'Tax Inclusive' && currentTaxObj) {
      updatedRate = new Decimal(item.rate).div(new Decimal(1).add(new Decimal(currentTaxObj.rate).div(100)))
    }

    const rowTotal = updatedRate.mul(item.quantity || 0)
    data.subTotal = data.subTotal.add(rowTotal)
    const rowDiscount = new Decimal(useCalcDiscount(item.discount_type, rowTotal.toNumber(), item.discount, props.discountOptions) || 0)

    if (currentTaxObj) {
      if (data.sameScheme === null && currentTaxObj && currentTaxObj.rate !== 0) {
        data.sameScheme = currentTaxObj.id
        data.taxObj = currentTaxObj
      } else if (data.sameScheme !== currentTaxObj?.id && currentTaxObj.rate !== 0) {
        data.sameScheme = null
      }
    }

    const mainDiscountAmount = new Decimal(useCalcDiscount(
      props.mainDiscount.discount_type,
      rowTotal.sub(rowDiscount).toNumber(),
      props.mainDiscount.discount,
      props.discountOptions,
    ) || 0)

    if (currentTaxObj) {
      let rowTax = new Decimal(0)
      if (props.mainDiscount.discount_type === 'Amount') {
        const discountAmount = new Decimal(props.mainDiscount.discount)
          .mul(rowTotal.div(data.addTotal))
        rowTax = rowTotal.sub(rowDiscount).sub(discountAmount).mul(new Decimal(currentTaxObj.rate).div(100))
      } else {
        rowTax = rowTotal.sub(rowDiscount).sub(mainDiscountAmount).mul(new Decimal(currentTaxObj.rate).div(100))
      }
      data.totalTax = data.totalTax.add(rowTax)
    }

    if (props.mainDiscount.discount_type === 'Amount') {
      if (index === 0) {
        data.discount = data.discount.add(rowDiscount).add(mainDiscountAmount)
      } else {
        data.discount = data.discount.add(rowDiscount)
      }
    } else {
      data.discount = data.discount.add(rowDiscount).add(mainDiscountAmount)
    }
  })

  if (typeof data.sameScheme === 'number' && data.taxObj) {
    data.taxName = `${data.taxObj.name || ''} @ ${data.taxObj.rate || ''}%`
    data.taxRate = data.taxObj.rate
  } else {
    data.taxName = 'Tax'
    data.taxRate = null
  }

  data.total = data.subTotal.sub(data.discount).add(data.totalTax)

  return {
    subTotal: data.subTotal.toNumber(),
    discount: data.discount.toNumber(),
    total: data.total.toNumber(),
    totalTax: data.totalTax.toNumber(),
    taxName: data.taxName,
    taxRate: data.taxRate,
  }
})

const addRow = () => {
  modalValue.value.push({
    ...defaultRowData,
  })
}

const removeRow = (index: number) => {
  if (props.errors || modalValue.value[index].id) {
    emit('deleteRowErr', index, modalValue.value[index]?.id ? modalValue.value[index] : null)
  }
  modalValue.value.splice(index, 1)
}

const onItemIdUpdate = async (itemId: number) => {
  if (itemId && !Object.hasOwn(itemPurchaseData.value, itemId)) {
    try {
      const data = await useApi(`/api/company/${route.params.company}/items/${itemId}/available-stock/`)
      itemPurchaseData.value[itemId] = data
    } catch (err) {
      console.error(err)
    }
  }

  const localPurchaseData = JSON.parse(JSON.stringify(itemPurchaseData.value))
  const COGSRows: Record<number, { totalCost: number | { status: string, message: string }, availableStock: number }> = {}

  modalValue.value.forEach((row, index) => {
    const currentItemId = row.item_id
    const availableStock = localPurchaseData[currentItemId] && localPurchaseData[currentItemId].length > 0
      ? localPurchaseData[currentItemId].reduce((accumulator: number, obj: any) => accumulator + obj.remaining_quantity, 0)
      : 0

    let currentCOGS: number | { status: string, message: string } = 0
    let quantity = row.quantity

    if (localPurchaseData[currentItemId] && localPurchaseData[currentItemId].length > 0) {
      for (let i = 0; quantity >= 0; i++) {
        const currentRow = localPurchaseData[currentItemId][i]
        if (currentRow.remaining_quantity > quantity) {
          currentRow.remaining_quantity = currentRow.remaining_quantity - quantity
          currentCOGS = new Decimal(quantity).mul(currentRow.rate).toNumber()
          break
        } else if (currentRow.remaining_quantity <= quantity) {
          quantity = quantity - currentRow.remaining_quantity
          currentCOGS = new Decimal(currentCOGS as number).add(
            new Decimal(currentRow.remaining_quantity).mul(currentRow.rate),
          ).toNumber()
          localPurchaseData[currentItemId][i].remaining_quantity = 0
          if (i + 1 === localPurchaseData[currentItemId].length) {
            if (quantity > 0) {
              currentCOGS = {
                status: 'error',
                message: 'The provided quantity exceeded the available quantity',
              }
              break
            } else {
              break
            }
          }
        }
      }
    } else {
      currentCOGS = {
        status: 'error',
        message: 'The provided quantity exceeded the available quantity',
      }
    }
    COGSRows[index] = { totalCost: currentCOGS, availableStock }
  })

  COGSData.value = COGSRows
}

if (props.usedIn === 'creditNote') {
  watch(totalDataComputed, (newValue) => {
    emit('updateVoucherMeta', newValue)
  })
}
</script>

<template>
  <q-card-section class="overflow-y-auto -mt-4">
    <q-card class="min-w-[700px] pt-6">
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-5 row">
            <div :class="usedIn === 'creditNote' ? 'col-10' : 'col-12'">
              Particular(s)
            </div>
            <div v-if="usedIn === 'creditNote'" class="col-2 text-center">
              Return
            </div>
          </div>
          <div class="col-2 text-center">
            Qty
          </div>
          <div class="col-2 text-center">
            Rate
          </div>
          <div class="col-2 text-center">
            Amount
          </div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <InvoiceRow
            v-if="modalValue[index]"
            v-model="modalValue[index]"
            :cogs-data="COGSData"
            :discount-options="discountOptions"
            :enable-row-description="props.enableRowDescription"
            :errors="!rowEmpty ? (Array.isArray(errors) ? errors[index] : null) : null"
            :has-challan="hasChallan"
            :index="index"
            :input-amount="props.inputAmount"
            :is-fifo="isFifo"
            :item-options="itemOptions"
            :missing-fields-config="missingFieldsConfig"
            :row-empty="(rowEmpty && index === 0) || false"
            :show-rate-quantity="props.showRateQuantity"
            :show-row-trade-discount="props.showRowTradeDiscount"
            :tax-options="props.taxOptions"
            :tax-type="taxType"
            :unit-options="unitOptions"
            :used-in="props.usedIn"
            @delete-row="(index) => removeRow(index)"
            @on-item-id-update="onItemIdUpdate"
          />
        </div>
        <div class="row q-py-sm">
          <div class="col-7 pt-2"></div>
          <div class="text-weight-bold text-grey-8 col-4 text-center">
            <div class="row q-pb-md">
              <div class="col-6 text-right">
                Sub Total
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-subtotal">
                <FormattedNumber type="currency" :value="totalDataComputed.subTotal" />
              </div>
            </div>
            <div v-if="totalDataComputed.discount" class="row q-pb-md">
              <div class="col-6 text-right">
                Discount
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-final-discount">
                <FormattedNumber type="currency" :value="totalDataComputed.discount" />
              </div>
            </div>
            <div v-if="totalDataComputed.totalTax" class="row q-pb-md">
              <div class="col-6 text-right" data-testid="computed-tax-name">
                {{ totalDataComputed.taxName }}
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-total-tax">
                <FormattedNumber type="currency" :value="totalDataComputed.totalTax" />
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-right">
                Total
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-total">
                <FormattedNumber type="currency" :value="totalDataComputed.total" />
              </div>
            </div>
          </div>
          <div class="col-1 text-center"></div>
        </div>
        <div>
          <q-btn
            outline
            class="q-px-lg q-py-ms"
            color="green"
            data-testid="add-row-btn"
            :disabled="hasChallan"
            @click="addRow"
          >
            Add Row
          </q-btn>
        </div>
      </div>
    </q-card>
  </q-card-section>
</template>
