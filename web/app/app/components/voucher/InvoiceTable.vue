<script>
import useCalcDiscount from '@/composables/useCalcDiscount.js'
import ItemAdd from '@/components/views/inventory/item/ItemForm.vue'
import InvoiceRow from './InvoiceRow.vue'

export default {
  props: {
    itemOptions: {
      type: Object,
      default: () => {
        return {
          results: [],
          pagination: {},
        }
      },
    },
    unitOptions: {
      type: Object,
      default: () => {
        return {
          results: [],
          pagination: {},
        }
      },
    },
    discountOptions: {
      type: Array,
      default: () => {
        return []
      },
    },
    taxOptions: {
      type: Array,
      default: () => {
        return []
      },
    },
    mainDiscount: {
      type: Object,
      default: () => {
        return { discount_type: null, discount: 0 }
      },
    },
    errors: {
      type: [Array, String],
      default: () => {
        return null
      },
    },
    usedIn: {
      type: String,
      default: () => {
        return null
      },
    },
    modelValue: {
      type: Array,
      default: () => [
        {
          discount: 0,
          quantity: 1,
          rate: '',
          item_id: null,
          unit_id: '',
          description: '',
          discount_type: null,
          tax_scheme_id: '',
          discount_id: null,
          trade_discount: false,
        },
      ],
    },
    enableRowDescription: {
      type: Boolean,
      default: () => false,
    },
    showRowTradeDiscount: {
      type: Boolean,
      default: () => false,
    },
    inputAmount: {
      type: Boolean,
      default: () => false,
    },
    showRateQuantity: {
      type: Boolean,
      default: () => true,
    },
    isFifo: {
      type: Boolean,
      default: () => false,
    },
    hasChallan: {
      type: Boolean,
      default: () => false,
    },
  },
  emits: ['update:modelValue', 'deleteRowErr', 'updateVoucherMeta'],
  setup(props, { emit }) {
    const route = useRoute()
    const modalValue = ref(props.modelValue)
    const rowEmpty = ref(false)
    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
      },
    )
    watch(
      () => props.errors,
      (newValue) => {
        if (newValue === 'This field is required.') rowEmpty.value = true
        else rowEmpty.value = false
      },
    )
    watch(
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true },
    )
    const totalDataComputed = computed(() => {
      const data = {
        subTotal: 0,
        discount: 0,
        total: 0,
        totalTax: 0,
        sameScheme: null,
        taxObj: null,
        taxName: null,
        taxRate: null,
        taxableAmount: 0,
        addTotal: 0,
      }
      modalValue.value.forEach((item) => {
        data.addTotal = data.addTotal + (item.rate || 0) * (item.quantity || 0)
      })
      modalValue.value.forEach((item, index) => {
        const rowTotal = (item.rate || 0) * (item.quantity || 0)
        data.subTotal = data.subTotal + rowTotal
        const rowDiscount = useCalcDiscount(item.discount_type, rowTotal, item.discount, props.discountOptions) || 0
        let currentTaxObj = null

        const taxOptions = Array.isArray(props.taxOptions) ? props.taxOptions : Object.hasOwn(props.taxOptions, 'results') ? props.taxOptions.results : []

        if (item.tax_scheme_id && taxOptions && taxOptions.length) {
          const taxindex = taxOptions.findIndex(taxItem => taxItem.id === item.tax_scheme_id)
          if (taxindex > -1) {
            currentTaxObj = taxOptions[taxindex]
          }
        }
        if (data.sameScheme !== false && currentTaxObj) {
          if (data.sameScheme === null && currentTaxObj && currentTaxObj.rate !== 0) {
            data.sameScheme = currentTaxObj.id
            data.taxObj = currentTaxObj
          } else if (data.sameScheme === currentTaxObj?.id || currentTaxObj.rate === 0) {
            // do nothing
          } else {
            data.sameScheme = false
          }
        }
        const mainDiscountAmount = useCalcDiscount(props.mainDiscount.discount_type, rowTotal - (rowDiscount || 0), props.mainDiscount.discount, props.discountOptions) || 0

        if (currentTaxObj) {
          let rowTax = 0
          if (props.mainDiscount.discount_type === 'Amount') {
            rowTax = (rowTotal - (rowDiscount || 0) - props.mainDiscount.discount * (rowTotal / data.addTotal)) * (currentTaxObj.rate / 100 || 0)
          } else {
            rowTax = (rowTotal - (rowDiscount || 0) - mainDiscountAmount) * (currentTaxObj.rate / 100 || 0)
          }
          data.totalTax = data.totalTax + rowTax
        }
        if (props.mainDiscount.discount_type === 'Amount') {
          if (index === 0) {
            data.discount = data.discount + rowDiscount + mainDiscountAmount
          } else {
            data.discount = data.discount + rowDiscount
          }
        } else {
          data.discount = data.discount + rowDiscount + mainDiscountAmount
        }
      })
      // tax
      if (typeof data.sameScheme === 'number' && data.taxObj) {
        data.taxName = `${data.taxObj.name || ''}` + ' @ ' + `${data.taxObj.rate || ''}` + '%'
        data.taxRate = data.taxObj.rate
      } else {
        data.taxName = 'Tax'
        data.taxRate = null
      }
      data.total = data.subTotal - data.discount + (data.totalTax || 0)
      return data
    })
    const amountComputed = computed(() => {
      const total = []
      modalValue.value.forEach((element) => {
        total.push((element.quantity || 0) * (element.rate || 0))
      })
      return total
    })
    const addRow = () => {
      modalValue.value.push({
        quantity: 1,
        rate: '',
        item_id: null,
        unit_id: '',
        description: '',
        discount: 0,
        discount_type: null,
        tax_scheme_id: '',
        discount_id: null,
      })
    }
    const removeRow = (index) => {
      if (props.errors || modalValue.value[index].id) {
        emit('deleteRowErr', index, modalValue.value[index]?.id ? modalValue.value[index] : null)
      }
      modalValue.value.splice(index, 1)
    }
    // For purchase rows Data of Items
    const itemPurchaseData = ref({})
    const COGSData = ref(null)
    const onItemIdUpdate = async (itemId) => {
      if (itemId && !itemPurchaseData.value.hasOwnProperty(itemId)) {
        try {
          const data = await useApi(`/api/company/${route.params.company}/items/${itemId}/available-stock/`)
          itemPurchaseData.value[itemId] = data
        } catch (err) {
          console.log(err)
        }
      }
      const localPurchaseData = JSON.parse(JSON.stringify(itemPurchaseData.value))
      const COGSRows = {}
      modalValue.value.forEach((row, index) => {
        const currentItemId = row.item_id
        // this calculates the total available stock for the selected item According to fifo
        const availableStock = localPurchaseData[currentItemId] && localPurchaseData[currentItemId].length > 0 ? localPurchaseData[currentItemId].reduce((accumulator, obj) => accumulator + obj.remaining_quantity, 0) : 0
        let currentCOGS = 0
        let quantity = row.quantity
        if (localPurchaseData[currentItemId] && localPurchaseData[currentItemId].length > 0) {
          for (let i = 0; quantity >= 0; i++) {
            const currentRow = localPurchaseData[currentItemId][i]
            if (currentRow.remaining_quantity > quantity) {
              currentRow.remaining_quantity = currentRow.remaining_quantity - quantity
              currentCOGS = currentCOGS + quantity * currentRow.rate
              break
            } else if (currentRow.remaining_quantity <= quantity) {
              quantity = quantity - currentRow.remaining_quantity
              currentCOGS = currentCOGS + currentRow.remaining_quantity * currentRow.rate
              localPurchaseData[currentItemId][i].remaining_quantity = 0
              if (i + 1 === localPurchaseData[currentItemId].length) {
                if (quantity > 0) {
                  currentCOGS = {
                    status: 'error',
                    message: 'The provided quantity exceeded the avaliable quantity',
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
            message: 'The provided quantity exceeded the avaliable quantity',
          }
        }
        COGSRows[index] = { totalCost: currentCOGS, availableStock }
      })
      COGSData.value = COGSRows
    }
    // For purchase rows Data of Items

    // to update voucher meta in Credit and debit Notes
    if (props.usedIn === 'creditNote') {
      watch(totalDataComputed, (newValue) => {
        emit('updateVoucherMeta', newValue)
      })
    }

    return {
      props,
      modalValue,
      amountComputed,
      addRow,
      removeRow,
      ItemAdd,
      totalDataComputed,
      InvoiceRow,
      useCalcDiscount,
      rowEmpty,
      itemPurchaseData,
      onItemIdUpdate,
      COGSData,
    }
  },
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
        <div v-for="(row, index) in modalValue" :key="row">
          <InvoiceRow
            v-if="modalValue[index]"
            v-model="modalValue[index]"
            :COGSData="COGSData"
            :discount-options="discountOptions"
            :enable-row-description="props.enableRowDescription"
            :errors="
              !rowEmpty
                ? Array.isArray(errors)
                  ? errors[index]
                  : null
                : null
            "
            :has-challan="hasChallan"
            :index="index"
            :input-amount="props.inputAmount"
            :is-fifo="isFifo"
            :item-options="itemOptions"
            :row-empty="(rowEmpty && index === 0) || false"
            :show-rate-quantity="props.showRateQuantity"
            :show-row-trade-discount="props.showRowTradeDiscount"
            :tax-options="taxOptions"
            :unit-options="unitOptions"
            :used-in="props.usedIn"
            @delete-row="(index) => removeRow(index)"
            @on-item-id-update="onItemIdUpdate"
          />
        </div>
        <div class="row q-py-sm">
          <div class="col-7 text-center text-left pt-2"></div>
          <div class="text-weight-bold text-grey-8 col-4 text-center">
            <div class="row q-pb-md">
              <div class="col-6 text-right">
                Sub Total
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-subtotal">
                {{ $nf(totalDataComputed.subTotal) }}
              </div>
            </div>
            <div v-if="totalDataComputed.discount" class="row q-pb-md">
              <div class="col-6 text-right">
                Discount
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-final-discount">
                {{ $nf(totalDataComputed.discount) }}
              </div>
            </div>
            <div v-if="totalDataComputed.totalTax" class="row q-pb-md">
              <div class="col-6 text-right" data-testid="computed-tax-name">
                {{ totalDataComputed.taxName }}
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-total-tax">
                {{ $nf(totalDataComputed.totalTax) }}
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-right">
                Total
              </div>
              <div class="col-6 q-pl-md" data-testid="computed-total">
                {{ $nf(totalDataComputed.total) }}
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
