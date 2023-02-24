<template>
  <q-card-section>
    <q-card>
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-5">Particular(s)</div>
          <div class="col-2 text-center">Qty</div>
          <div class="col-2 text-center">Rate</div>
          <div class="col-2 text-center">Amount</div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="`invoice-row-${index}`">
          <InvoiceRow v-model="modalValue[index]" :itemOptions="itemOptions" :unitOptions="unitOptions"
            :taxOptions="taxOptions" :discountOptions="discountOptions" :index="index"
            :rowEmpty="(rowEmpty && index === 0) || false" @deleteRow="(index) => removeRow(index, modalValue)" :errors="
              !rowEmpty ? (Array.isArray(errors) ? errors[index] : null) : null
            " />
        </div>
        <div class="row q-py-sm">
          <div class="col-7 text-center"></div>
          <div class="text-weight-bold text-grey-8 col-4 text-center">
            <div class="row q-pb-md">
              <div class="col-6 text-right">Sub Total</div>
              <div class="col-6 q-pl-md">
                {{ parseFloat(totalDataComputed.subTotal) }}
              </div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.discount">
              <div class="col-6 text-right">Discount</div>
              <div class="col-6 q-pl-md">
                {{ parseFloat(totalDataComputed.discount.toFixed(2)) }}
              </div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.totalTax">
              <div class="col-6 text-right">
                {{ totalDataComputed.taxName }}
              </div>
              <div class="col-6 q-pl-md">
                {{ parseFloat(totalDataComputed.totalTax.toFixed(2)) }}
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-right">Total</div>
              <div class="col-6 q-pl-md">
                {{ parseFloat(totalDataComputed.total.toFixed(2)) }}
              </div>
            </div>
          </div>
          <div class="col-1 text-center"></div>
        </div>
        <div>
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms">Add Row</q-btn>
        </div>
      </div>
    </q-card>
    {{ errors }} --errors
    {{ totalDataComputed }} --tdata
  </q-card-section>
</template>

<script>
import ItemAdd from 'src/pages/inventory/item/ItemAdd.vue'
import InvoiceRow from './InvoiceRow.vue'
import useCalcDiscount from 'src/composables/useCalcDiscount.js'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  props: {
    itemOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    unitOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    discountOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    taxOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    mainDiscount: {
      type: Object,
      default: () => {
        return { discount_type: null, discount: 0 }
      },
    },
    errors: {
      type: Array || String,
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
          item_id: '',
          unit_id: '',
          description: '',
          discount_type: null,
          tax_scheme_id: '',
          taxObj: null,
          discount_id: null,
        },
      ],
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const rows = ref(1)
    const modalValue = ref(props.modelValue)
    const rowEmpty = ref(false)
    watch(
      () => props.modelValueProps,
      (newValue) => {
        modalValue.value = newValue
      }
    )
    watch(
      () => props.errors,
      (newValue) => {
        if (newValue === 'This field is required.') rowEmpty.value = true
        else rowEmpty.value = false
      }
    )
    watch(
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
    const totalDataComputed = computed(() => {
      let data = {
        subTotal: 0,
        discount: 0,
        total: 0,
        totalTax: 0,
        sameScheme: null,
        taxObj: null,
        taxName: null,
        taxRate: null,
        taxableAmount: 0,
      }
      modalValue.value.forEach((item, index) => {
        console.log(item, 'in loop')
        const rowTotal = (item.rate || 0) * (item.quantity || 0)
        data.subTotal = data.subTotal + rowTotal
        const rowDiscount = useCalcDiscount(
          item.discount_type,
          rowTotal,
          item.discount,
          props.discountOptions
        ) || 0
        if (data.sameScheme !== false && item.taxObj) {
          if (data.sameScheme === null && item.taxObj) {
            data.sameScheme = item.taxObj.id
            data.taxObj = item.taxObj
          } else if (data.sameScheme === item.taxObj?.id) {
          } else data.sameScheme = false
        }
        const mainDiscountAmount =
          useCalcDiscount(
            props.mainDiscount.discount_type,
            rowTotal - (rowDiscount || 0),
            props.mainDiscount.discount,
            props.discountOptions
          ) || 0
        data.discount = data.discount + rowDiscount + mainDiscountAmount
        if (item.taxObj) {
          const rowTax =
            (rowTotal - (rowDiscount || 0) - mainDiscountAmount) *
            (item.taxObj.rate / 100 || 0)
          data.totalTax = data.totalTax + rowTax
        }
      })
      // tax
      if (typeof data.sameScheme === 'number' && data.taxObj) {
        data.taxName =
          `${data.taxObj.name || ''}` +
          ' @ ' +
          `${data.taxObj.rate || ''}` +
          '%'
        data.taxRate = data.taxObj.rate
      } else {
        data.taxName = 'Tax'
        data.taxRate = null
      }
      // clac total discount
      // data.discount =
      //   (data.discount || 0) +
      //   (useCalcDiscount(
      //     props.mainDiscount.discount_type,
      //     data.subTotal - data.discount,
      //     props.mainDiscount.discount,
      //     props.discountOptions
      //   ) || 0)
      data.total = data.subTotal - data.discount + (data.totalTax || 0)
      return data
    })
    const amountComputed = computed(() => {
      let total = []
      modalValue.value.forEach((element) => {
        total.push((element.quantity || 0) * (element.rate || 0))
      })
      return total
    })
    const addRow = () => {
      modalValue.value.push({
        quantity: '',
        rate: '',
        item_id: '',
        unit_id: '',
        description: '',
        discount: 0,
        discount_type: null,
        tax_scheme_id: '',
        discount_id: null,
      })
    }
    const removeRow = (index, rows) => {
      rows.splice(index, 1)
    }
    return {
      rows,
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
    }
  },
}
</script>
