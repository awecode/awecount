<template>
  <div :class="usedInPos ? '-mt-12' : ''">
    <div class="row q-col-gutter-md no-wrap">
      <div class="col-5 row">
        <div :class="usedIn === 'creditNote' ? 'col-10' : 'col-12'" data-testid="item">
          <n-auto-complete v-if="!usedInPos" v-model="modalValue.item_id" :options="itemOptions" label="Item"
            :error="errors?.item_id ? errors?.item_id[0] : rowEmpty ? 'Item is required' : ''" :modal-component="usedInPos || hasChallan
              ? false
              : checkPermissions('InventoryAccountCreate')
                ? ItemAdd
                : null
              " :disabled="usedInPos || hasChallan" />
          <q-input v-else :label="usedInPos ? '' : 'Item'" disable :modelValue="modelValue.name"></q-input>
        </div>
        <div v-if="usedIn === 'creditNote'" class="col-2 row justify-center">
          <q-checkbox v-model="modalValue.is_returned" :false-value="null">
          </q-checkbox>
        </div>
      </div>
      <div class="col-2">
        <span v-if="showRateQuantity">
          <q-input v-model.number="modalValue.quantity" :label="usedInPos ? '' : 'Quantity'"
            :error-message="errors?.quantity ? errors.quantity[0] : null" :error="errors?.quantity ? true : false"
            type="number" :disable="hasChallan" data-testid="quantity-input">
            <template v-if="isFifo && COGSData?.hasOwnProperty(index)" v-slot:append>
              <q-icon v-if="COGSData[index].totalCost.status === 'error'" color="orange" name="mdi-alert">
                <q-tooltip>
                  {{ COGSData[index].totalCost.message }}
                  <br>
                  Available Quantity {{ COGSData[index].availableStock }}
                </q-tooltip>
              </q-icon>
              <span v-else class="text-sm mt-4 text-blue-400">
                <q-tooltip>
                  Available Stock
                </q-tooltip>
                {{ COGSData[index].availableStock }}
              </span>
            </template>
          </q-input>
        </span>
      </div>
      <div class="col-2">
        <div v-if="showRateQuantity">
          <q-input v-model.number="modalValue.rate" :label="usedInPos ? '' : 'Rate'"
            :error-message="errors?.rate ? errors.rate[0] : null" :error="errors?.rate ? true : false" type="number"
            data-testid="rate-input">
            <template v-if="isFifo && COGSData?.hasOwnProperty(index)" v-slot:append>
              <span v-if="COGSData[index].totalCost.status != 'error'" class="text-sm mt-4 text-blue-400">
                <q-tooltip>
                  Cost Rate as per Fifo.
                </q-tooltip>
                {{ $nf(COGSData[index].totalCost / modalValue.quantity) }}</span>
              <!-- <q-icon v-else color="orange" name="mdi-alert">
                  <q-tooltip>
                    {{ COGSData[index].message }}
                  </q-tooltip>
                </q-icon> -->
            </template>
          </q-input>
        </div>
      </div>
      <div v-if="inputAmount" class="col-2">
        <!-- <span class="">{{ amountComputed }}</span> -->
        <q-input v-model="amountComputed" label="Amount" @change="onAmountInput" data-testid="amount-input">
          <template v-if="isFifo && COGSData?.hasOwnProperty(index) && COGSData[index].totalCost.status != 'error'"
            v-slot:append>
            <span class="text-sm mt-4 text-blue-400">
              <q-tooltip>
                Total Cost Price as per Fifo.
              </q-tooltip>
              {{ $nf(COGSData[index].totalCost) }}</span>
          </template>
        </q-input>
        <!-- <q-input v-model="amountComputed" disable label="Amount"></q-input> -->
      </div>
      <div v-else class="col-2 row justify-center items-center">
        <span class="" data-testid="amount-input">{{ amountComputed }}
          <span class="relative bg-red-200"
            v-if="isFifo && COGSData?.hasOwnProperty(index) && COGSData[index].totalCost.status != 'error'">
            <span class="text-sm ml-2 text-blue-400 absolute top-1/2 -right-0 -translate-y-1/2">
              <q-tooltip>
                Total Cost Price as per Fifo.
              </q-tooltip>
              {{ $nf(COGSData[index].totalCost) }}</span>
          </span>
        </span>
        <!-- <q-input v-model="amountComputed" disable label="Amount"></q-input> -->
      </div>
      <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
        <q-btn flat class="q-pa-sm focus-highLight" color="transparent" @click="() => (expandedState = !expandedState)"
          data-testid="expand-btn">
          <q-icon name="mdi-arrow-expand" size="20px" color="green" class="cursor-pointer">
            <q-tooltip>Expand</q-tooltip>
          </q-icon>
        </q-btn>
        <q-btn flat @click="() => deleteRow(index)" class="q-pa-sm focus-highLight" color="transparent"
          :disable="hasChallan" data-testid="row-delete-btn">
          <q-icon name="delete" size="20px" color="negative" class="cursor-pointer"></q-icon>
        </q-btn>
      </div>
    </div>
    <!-- <div v-if="isFifo && COGSData?.hasOwnProperty(index)" class="pb-2">
      <div v-if="COGSData[index].status != 'error'" class="row text-blue-4">
        <div class="col-5">Average Cost:</div>
        <div class="col-2"></div>
        <div class="col-2 q-pl-sm">
          {{ $nf(COGSData[index] / modalValue.quantity) }}
        </div>
        <div class="col-2 text-center">{{ COGSData[index] }}</div>
      </div>
      <div v-else class="row text-orange-5">
        <div class="col-5">Error:</div>
        <div class="col-1"></div>
        <div class="col-5 q-pl-sm text-right">
          {{ COGSData[index].message }}
        </div>
      </div>
    </div> -->
    <div v-if="expandedState">
      <div class="row q-col-gutter-md q-px-lg">
        <div class="col-grow">
          <q-select v-model="modalValue.unit_id" :options="unitOptions" label="Unit" option-value="id" option-label="name"
            emit-value map-options :error-message="errors?.unit_id ? errors.unit_id[0] : null"
            :error="errors?.unit_id ? true : false" data-testid="unit-select" />
        </div>
        <div class="col-5">
          <div class="row q-col-gutter-md">
            <div :class="['Amount', 'Percent'].includes(modalValue.discount_type)
              ? 'col-5'
              : 'col-12'
              " data-testid="row-discount-type-div">
              <n-auto-complete v-model="modalValue.discount_type" label="Discount" :options="discountOptions">
              </n-auto-complete>
            </div>
            <div :class="showRowTradeDiscount ? 'col-3' : 'col-6'" v-if="modalValue.discount_type === 'Amount' ||
              modalValue.discount_type === 'Percent'
              ">
              <q-input v-model.number="modalValue.discount" label="Discount"
                :error-message="errors?.discount ? errors.discount[0] : null" :error="errors?.discount ? true : false"
                data-testid="row-discount-input"></q-input>
            </div>
            <div class="col-3 row" v-if="['Amount', 'Percent'].includes(modalValue.discount_type) &&
              showRowTradeDiscount
              ">
              <q-checkbox v-model="modalValue.trade_discount" label="Trade Discount?"
                data-testid="row-trade-discount-checkbox"></q-checkbox>
            </div>
          </div>
        </div>
        <div class="col-3">
          <q-select v-model="modalValue.tax_scheme_id" :options="taxOptions" label="Tax" option-value="id"
            option-label="name" emit-value map-options :error="errors?.tax_scheme_id ? true : null" :error-message="errors?.tax_scheme_id ? 'This field is required' : null
              " data-testid="row-tax-select" />
        </div>
      </div>
      <div v-if="$route.params.id
        ? (!!modalValue.item_id || !!modalValue.itemObj) &&
        enableRowDescription
        : !!modalValue.itemObj && enableRowDescription
        ">
        <q-input label="Description" v-model="modalValue.description" type="textarea" class="q-mb-lg"
          data-testid="row-description-input">
        </q-input>
      </div>
    </div>
  </div>
</template>

<script>
import ItemAdd from 'src/pages/inventory/item/ItemAdd.vue'
import checkPermissions from 'src/composables/checkPermissions'
export default {
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
      type: Array,
      default: () => {
        return []
      },
    },
    errors: {
      type: Object,
      default: () => {
        return null
      },
    },
    rowEmpty: {
      type: Boolean,
      default: () => false,
    },
    usedIn: {
      type: String,
      default: () => {
        return null
      },
    },
    usedInPos: {
      type: Boolean,
      default: () => false,
    },
    taxOptions: {
      type: Array,
      default: () => {
        return []
      },
    },
    modelValue: {
      type: Object,
      default: () => {
        return {
          quantity: 1,
          rate: '',
          item_id: null,
          unit_id: null,
          description: '',
          discount: 0,
          discount_type: null,
          itemObj: null,
          tax_scheme_id: '',
          taxObj: null,
          discount_id: null,
          trade_discount: false,
        }
      },
    },
    index: {
      type: Number,
      default: () => null,
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
    COGSData: {
      type: Object,
      default: () => null,
    },
    hasChallan: {
      type: Boolean,
      default: () => false,
    },
  },

  emits: ['update:modelValue', 'deleteRow', 'onItemIdUpdate'],
  setup(props, { emit }) {
    const route = useRoute()
    const expandedState = ref(false)
    const modalValue = ref(props.modelValue)
    const selectedTax = ref(null)
    const amountComputed = computed(
      () =>
        Math.round(
          (modalValue.value.rate || 0) * (modalValue.value.quantity || 0) * 100
        ) / 100
    )
    const selectedItem = ref(null)
    const updateTaxObj = () => {
      const taxindex = props.taxOptions.findIndex(
        (item) => item.id === props.modelValue.tax_scheme_id
      )
      if (taxindex > -1) {
        selectedTax.value = props.taxOptions[taxindex]
        nextTick(() => (modalValue.value.taxObj = props.taxOptions[taxindex]))
      }
    }

    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
        emit('update:modelValue', newValue)
      }
    )
    watch(
      () => modalValue.value,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
    watch(
      () => props.modelValue.item_id,
      (newValue) => {
        if (!!props.itemOptions && !!newValue) {
          const index = props.itemOptions.findIndex(
            (item) => item.id === newValue
          )
          const itemObject = props.itemOptions[index]
          modalValue.value.itemObj = itemObject
          modalValue.value.item_id = itemObject.id
          modalValue.value.description = itemObject.description
          modalValue.value.rate = itemObject.rate
          modalValue.value.unit_id = itemObject.unit_id
          modalValue.value.tax_scheme_id = itemObject.tax_scheme_id
        }
      }
    )
    watch(
      () => props.modelValue.tax_scheme_id,
      () => updateTaxObj()
    )
    watch(
      () => props.taxOptions,
      () => updateTaxObj()
    )
    watch(
      () => props.errors,
      (newValue) => {
        if (newValue?.tax_scheme_id || newValue?.unit_id)
          expandedState.value = true
      }
    )
    watch(
      () => props.modelValue.discount_type,
      (newValue) => {
        if (typeof newValue === 'number') {
          const index = props.discountOptions.findIndex(
            (item) => newValue === item.id
          )
          modalValue.value.discountObj = props.discountOptions[index]
        } else if (newValue === null) {
          modalValue.value.discountObj = null
          modalValue.value.discount = null
        } else modalValue.value.discountObj = null
      }
    )
    const deleteRow = (index) => {
      emit('deleteRow', index)
    }
    onMounted(() => {
      if (props.usedIn === 'creditNote') modalValue.value.is_returned = true
    })
    const onAmountInput = (amount) => {
      if (
        amount !==
        (modalValue.value.rate || 0) * (modalValue.value.quantity || 1)
      ) {
        if (!modalValue.value.quantity) modalValue.value.quantity = 1
        modalValue.value.rate = amount / modalValue.value.quantity
      }
    }
    if (props.isFifo && props.usedIn === 'sales' && !route.params.id) {
      watch(
        () => modalValue.value.item_id,
        (newValue) => {
          if (modalValue.value.item_id) emit('onItemIdUpdate', newValue)
        }
      )
      watch(
        () => modalValue.value.quantity,
        () => {
          if (modalValue.value.item_id) emit('onItemIdUpdate')
        }
      )
    }
    return {
      ItemAdd,
      expandedState,
      modalValue,
      amountComputed,
      selectedItem,
      selectedTax,
      deleteRow,
      checkPermissions,
      onAmountInput,
    }
  },
}
</script>
