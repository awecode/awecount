<template>
  <q-card-section>
    <q-card>
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
          <div class="col-2 text-center">Qty</div>
          <div class="col-2 text-center">Rate</div>
          <div class="col-2 text-center">Amount</div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <InvoiceRow v-if="modalValue[index]" :usedIn="props.usedIn" v-model="modalValue[index]"
            :itemOptions="itemOptions" :unitOptions="unitOptions" :taxOptions="taxOptions"
            :discountOptions="discountOptions" :index="index" :rowEmpty="(rowEmpty && index === 0) || false"
            @deleteRow="(index) => removeRow(index)" :errors="!rowEmpty ? (Array.isArray(errors) ? errors[index] : null) : null
              " :usedInPos="props.usedInPos" :enableRowDescription="props.enableRowDescription"
            :showRowTradeDiscount="props.showRowTradeDiscount" />
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
                <!-- {{ totalDataComputed.discount }} -->
                {{ Math.round(totalDataComputed.discount * 100) / 100 }}
              </div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.totalTax">
              <div class="col-6 text-right">
                {{ totalDataComputed.taxName }}
              </div>
              <div class="col-6 q-pl-md">
                {{ Math.round(totalDataComputed.totalTax * 100) / 100 }}
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-right">Total</div>
              <div class="col-6 q-pl-md">
                {{ Math.round(totalDataComputed.total * 100) / 100 }}
              </div>
            </div>
          </div>
          <div class="col-1 text-center"></div>
        </div>
        <div>
          <q-btn @click="addRow" v-if="!usedInPos" color="green" outline class="q-px-lg q-py-ms">Add Row</q-btn>
        </div>
      </div>
    </q-card>
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
      type: Array,
      default: () => {
        return []
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
      type: Array || String,
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
          taxObj: null,
          discount_id: null,
        },
      ],
    },
    usedInPos: {
      type: Boolean,
      default: () => false,
    },
    enableRowDescription: {
      type: Boolean,
      default: () => false,
    },
    showRowTradeDiscount: {
      type: Boolean,
      default: () => false,
    },
  },
  emits: ['update:modelValue', 'deleteRowErr'],
  setup(props, { emit }) {
    const modalValue = ref(props.modelValue)
    const rowEmpty = ref(false)
    watch(
      () => props.modelValue,
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
        addTotal: 0,
      }
      modalValue.value.forEach((item) => {
        data.addTotal = data.addTotal + (item.rate || 0) * (item.quantity || 0)
      })
      modalValue.value.forEach((item, index) => {
        const rowTotal = (item.rate || 0) * (item.quantity || 0)
        data.subTotal = data.subTotal + rowTotal
        const rowDiscount =
          useCalcDiscount(
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
        let mainDiscountAmount =
          useCalcDiscount(
            props.mainDiscount.discount_type,
            rowTotal - (rowDiscount || 0),
            props.mainDiscount.discount,
            props.discountOptions
          ) || 0

        // preventing from mainDiscount amount from being added Twice

        // checking if tax is selected manually
        // if (item.tax_scheme_id) {
        //   let rowTax = 0
        //   if (props.mainDiscount.discount_type === 'Amount') {
        //     rowTax =
        //       (rowTotal -
        //         (rowDiscount || 0) -
        //         props.mainDiscount.discount * (rowTotal / data.addTotal)) *
        //       (item.taxObj.rate / 100 || 0)
        //   } else {
        //     rowTax =
        //       (rowTotal - (rowDiscount || 0) - mainDiscountAmount) *
        //       (item.taxObj.rate / 100 || 0)
        //   }
        //   data.totalTax = data.totalTax + rowTax
        // }
        // checking if tax is selected coming automaticaly with item
        if (item.taxObj) {
          let rowTax = 0
          if (props.mainDiscount.discount_type === 'Amount') {
            rowTax =
              (rowTotal -
                (rowDiscount || 0) -
                props.mainDiscount.discount * (rowTotal / data.addTotal)) *
              (item.taxObj.rate / 100 || 0)
          } else {
            rowTax =
              (rowTotal - (rowDiscount || 0) - mainDiscountAmount) *
              (item.taxObj.rate / 100 || 0)
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
      // if (props.mainDiscount.discount_type === 'Amount') {
      //   modalValue.value.forEach((item, index) => {
      //     console.log(data.subTotal, index)
      //     // const rowTotal = (())
      //   })
      // }
      // data.totalTax = data.subTotal - data.discount *
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
      if (props.errors || modalValue.value[index].id)
        emit(
          'deleteRowErr',
          index,
          modalValue.value[index]?.id ? modalValue.value[index] : null
        )
      modalValue.value.splice(index, 1)
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
    }
  },
}
</script>
