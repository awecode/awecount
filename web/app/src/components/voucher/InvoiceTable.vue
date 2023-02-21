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
          <InvoiceRow
            v-model="modalValue[index]"
            :itemOptions="itemOptions"
            :unitOptions="unitOptions"
            :taxOptions="taxOptions"
            :discountOptions="discountOptions"
          />
        </div>
        <div class="q-px-lg row items-end">
          <div class="col-grow"></div>
          <div class="text-weight-bold text-grey-8 col-4">
            <div class="row q-pb-md">
              <div class="col-6 text-center">Sub Total</div>
              <div>{{ totalDataComputed.subTotal }}</div>
            </div>
            <div class="row q-pb-md" v-if="totalDataComputed.discount">
              <div class="col-6 text-center">Discount</div>
              <div>
                {{ totalDataComputed.discount }}
              </div>
            </div>
            <div class="row q-pb-md">
              <div class="col-6 text-center">Total</div>
              <div>
                {{ 150 }}
              </div>
            </div>
          </div>
        </div>
        <div>
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms"
            >Add Row</q-btn
          >
        </div>
      </div>
      {{ totalDataComputed }}--dis 0
    </q-card>
  </q-card-section>
</template>

<script>
import ItemAdd from 'src/pages/inventory/item/ItemAdd.vue'
import InvoiceRow from './InvoiceRow.vue'
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
        // console.log('watcher invoked')
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
    const totalDataComputed = computed(() => {
      let data = {
        subTotal: 0,
        discount: 0,
      }
      console.log(props.modelValueProps)
      modalValue.value.forEach((item, index) => {
        data.subTotal = item.quantity
        if (item.discount_type === 'Percent') {
          data.discount =
            data.discount + amountComputed.value[index] * (item.discount / 100)
        } else if (item.discount_type === 'Amount')
          data.discount = data.discount + item.discount
      })
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
    }
  },
}
</script>
