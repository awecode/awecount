<template>
  <q-card-section>
    <q-card>
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-5">Particular(s)</div>
          <div class="col-2 text-center">Qty</div>
          <div class="col-2 text-center">Rate</div>
          <div class="col-2 text-center">Amnt</div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <InvoiceRow v-model="modalValue[index]" :itemOptions="itemOptions" :unitOptions="unitOptions"
            :taxOptions="taxOptions" :discountOptions="discountOptions" />
        </div>
        <div class="q-px-lg row items-end">
          <div class="col-grow"></div>
          <div class="text-weight-bold text-grey-8 col-4">
            <div class="row q-pb-md">
              <div class="col-6 text-center">Sub Total</div>
              <div>{{ parseFloat(totalDataComputed.subTotal) }}</div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.discount">
              <div class="col-6 text-center">Discount</div>
              <div>
                {{ parseFloat(totalDataComputed.discount) }}
              </div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.totalTax">
              <div class="col-6 text-center">
                {{ totalDataComputed.taxName }}
              </div>
              <div>
                {{ parseFloat(totalDataComputed.totalTax.toFixed(2)) }}
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-center">Total</div>
              <div>
                {{ parseFloat(totalDataComputed.total.toFixed(2)) }}
              </div>
            </div>
          </div>
        </div>
        <div>
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms">Add Row</q-btn>
        </div>
      </div>
      {{ props }}--maindiscount
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

    modelValue: {
      type: Array,
      default: () => [
        {
          discount: '',
          quantity: '',
          rate: '',
          item_id: '',
          unit_id: '',
          description: '',
          discount: '',
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
    const expandedState = ref([false])
    const modalValue = ref(props.modelValue)
    watch(
      () => props.modelValueProps,
      (newValue) => {
        modalValue.value = newValue
      },
      {
        deep: true,
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
      }
      modalValue.value.forEach((item, index) => {
        const rowTotal = (item.value?.rate || 0) * (item.value?.quantity || 0)
        data.subTotal = data.subTotal + rowTotal
        const rowDiscount = useCalcDiscount(
          item.value?.discount_type,
          rowTotal,
          item.value?.discount,
          props.discountOptions
        )
        data.discount = data.discount + rowDiscount
        if (data.sameScheme !== false && item.value?.taxObj) {
          if (data.sameScheme === null && item.value.taxObj) {
            data.sameScheme = item.value.taxObj.id
            data.taxObj = item.value.taxObj
          } else if (data.sameScheme === item.value?.taxObj.id) {
          } else data.sameScheme = false
        }
        const mainDiscountAmount = useCalcDiscount(
          props.mainDiscount.discount_type,
          data.subTotal - data.discount,
          props.mainDiscount.discount,
          props.discountOptions
        ) || 0
        console.log(mainDiscountAmount, 'mainDiscountAmount')
        if (item.value?.taxObj) {
          const rowTax =
            (rowTotal - mainDiscountAmount - (rowDiscount || 0)) *
            (item.value.taxObj.rate / 100 || 0)
          // * (100 - props.mainDiscount)
          console.log(
            rowTax,
            data.discount,
            item.value.taxObj.rate,
            rowDiscount
          )
          data.totalTax = data.totalTax + rowTax
        }
      })
      // tax
      if (typeof data.sameScheme === 'number' && data.taxObj) {
        data.taxName =
          `${data.taxObj.name || ''}` + ' @ ' + `${data.taxObj.rate || ''}` + '%'
        data.taxRate = data.taxObj.rate
      } else {
        data.taxName = 'Tax'
        data.taxRate = null
      }
      // clac main discount
      data.discount =
        (data.discount || 0) +
        (useCalcDiscount(
          props.mainDiscount.discount_type,
          data.subTotal - data.discount,
          props.mainDiscount.discount,
          props.discountOptions
        ) || 0)
      // console.log(data.totalTax)
      data.total = data.subTotal - data.discount + (data.totalTax || 0)
      return data
    })
    // const taxObhComputed = computed(() => {
    //   if (tax)
    // })
    const amountComputed = computed(() => {
      let total = []
      modalValue.value.forEach((element) => {
        total.push((element.quantity || 0) * (element.rate || 0))
      })
      return total
    })
    const addRow = () => {
      modalValue.value.push({
        discount: '',
        quantity: '',
        rate: '',
        item_id: '',
        unit_id: '',
        description: '',
        discount: '',
        discount_type: null,
        tax_scheme_id: '',
        discount_id: null,
      })
      expandedState.value.push(false)
    }
    const removeRow = (index) => {
      modalValue.value.splice(index, 1)
      expandedState.value.splice(index, 1)
    }
    const changeExpandedState = (index) => {
      expandedState.value[index] = !expandedState.value[index]
    }
    return {
      rows,
      props,
      expandedState,
      modalValue,
      amountComputed,
      addRow,
      removeRow,
      ItemAdd,
      changeExpandedState,
      totalDataComputed,
      InvoiceRow,
      useCalcDiscount,
    }
  },
}
</script>
