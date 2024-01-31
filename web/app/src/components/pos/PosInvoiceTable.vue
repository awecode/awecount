<template>
  <q-card-section class="overflow-y-auto -mt-4">
    <q-card :class="usedInPos ? 'min-w-[550px]' : 'min-w-[700px]'" class="pt-6">
      <div :class="usedInPos ? 'q-px-lg' : 'q-pa-lg'" class="q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap mb-2">
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
        <div v-for="(row, index) in modalValue" :key="row">
          <InvoiceRow v-if="modalValue[index]" v-model="modalValue[index]" :unitOptions="unitOptions"
            :taxOptions="taxOptions" :discountOptions="discountOptions" :index="index"
            :rowEmpty="(rowEmpty && index === 0) || false" @deleteRow="(index) => removeRow(index)"
            :errors="!rowEmpty ? (Array.isArray(errors) ? errors[index] : null) : null" :usedInPos="true"
            :enableRowDescription="props.enableRowDescription" :showRowTradeDiscount="false" :inputAmount="false"
            :showRateQuantity="true" @onItemIdUpdate="onItemIdUpdate" />
        </div>
      </div>
    </q-card>
  </q-card-section>
</template>

<script>
import useCalcDiscount from 'src/composables/useCalcDiscount.js'
import InvoiceRow from '../voucher/InvoiceRow.vue'
export default {
  props: {
    unitOptions: {
      type: Object,
      default: () => {
        return {};
      },
    },
    discountOptions: {
      type: Object,
      default: () => {
        return {};
      },
    },
    taxOptions: {
      type: Array,
      default: () => {
        return [];
      },
    },
    mainDiscount: {
      type: Object,
      default: () => {
        return { discount_type: null, discount: 0 };
      },
    },
    errors: {
      type: Array || String,
      default: () => {
        return null;
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
          trade_discount: false,
        },
      ],
    },
    inputAmount: {
      type: Boolean,
      default: () => false,
    }
  },
  emits: ['update:modelValue', 'deleteRowErr', '@updateTableData'],
  setup(props, { emit }) {
    const modalValue = ref(props.modelValue);
    const rowEmpty = ref(false);
    watch(() => props.modelValue, (newValue) => {
      modalValue.value = newValue;
    });
    watch(() => props.errors, (newValue) => {
      if (newValue === 'This field is required.')
        rowEmpty.value = true;
      else
        rowEmpty.value = false;
    });
    watch(() => props.errors, (newValue) => {
      if (newValue === 'This field is required.')
        rowEmpty.value = true;
      else
        rowEmpty.value = false;
    });
    watch(() => modalValue, (newValue) => {
      emit('update:modelValue', newValue);
    }, { deep: true });
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
      };
      modalValue.value.forEach((item) => {
        data.addTotal = data.addTotal + (item.rate || 0) * (item.quantity || 0);
      });
      modalValue.value.forEach((item, index) => {
        const rowTotal = (item.rate || 0) * (item.quantity || 0);
        data.subTotal = data.subTotal + rowTotal;
        const rowDiscount = useCalcDiscount(item.discount_type, rowTotal, item.discount, props.discountOptions) || 0;
        const rowTaxObj = findtaxObj(item.tax_scheme_id)
        if (data.sameScheme !== false && rowTaxObj) {
          if (data.sameScheme === null &&
            rowTaxObj &&
            rowTaxObj.rate != 0) {
            data.sameScheme = rowTaxObj.id;
            data.taxObj = rowTaxObj;
          }
          else if (data.sameScheme === rowTaxObj?.id ||
            rowTaxObj.rate === 0) {
          }
          else
            data.sameScheme = false;
        }
        let mainDiscountAmount = useCalcDiscount(props.mainDiscount.discount_type, rowTotal - (rowDiscount || 0), props.mainDiscount.discount, props.discountOptions) || 0;
        if (rowTaxObj) {
          let rowTax = 0;
          if (props.mainDiscount.discount_type === 'Amount') {
            rowTax =
              (rowTotal -
                (rowDiscount || 0) -
                props.mainDiscount.discount * (rowTotal / data.addTotal)) *
              (rowTaxObj.rate / 100 || 0);
          }
          else {
            rowTax =
              (rowTotal - (rowDiscount || 0) - mainDiscountAmount) *
              (rowTaxObj.rate / 100 || 0);
          }
          data.totalTax = data.totalTax + rowTax;
        }
        if (props.mainDiscount.discount_type === 'Amount') {
          if (index === 0) {
            data.discount = data.discount + rowDiscount + mainDiscountAmount;
          }
          else {
            data.discount = data.discount + rowDiscount;
          }
        }
        else {
          data.discount = data.discount + rowDiscount + mainDiscountAmount;
        }
      });
      // tax
      if (typeof data.sameScheme === 'number' && data.taxObj) {
        data.taxName =
          `${data.taxObj.name || ''}` +
          ' @ ' +
          `${data.taxObj.rate || ''}` +
          '%';
        data.taxRate = data.taxObj.rate;
      }
      else {
        data.taxName = 'Tax';
        data.taxRate = null;
      }
      data.total = data.subTotal - data.discount + (data.totalTax || 0);
      return data;
    });
    const amountComputed = computed(() => {
      let total = [];
      modalValue.value.forEach((element) => {
        total.push((element.quantity || 0) * (element.rate || 0));
      });
      return total;
    });
    const removeRow = (index) => {
      if (props.errors || modalValue.value[index].id)
        emit('deleteRowErr', index, modalValue.value[index]?.id ? modalValue.value[index] : null);
      modalValue.value.splice(index, 1);
    };
    watch(() => totalDataComputed.value, (newValue) => {
      emit('updateTableData', newValue);
    })
    const findtaxObj = (id) => {
      if (!id || !props.taxOptions.length > 0) return null
      else {
        const taxindex = props.taxOptions.findIndex(
          (item) => item.id === id
        )
        if (taxindex >= 0) return props.taxOptions[taxindex]
        else return null
      }
    }
    return {
      props,
      modalValue,
      amountComputed,
      removeRow,
      totalDataComputed,
      useCalcDiscount,
      rowEmpty
    };
  },
  components: { InvoiceRow }
}
</script>
