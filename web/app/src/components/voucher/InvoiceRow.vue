<script>
import checkPermissions from 'src/composables/checkPermissions'
import ItemForm from 'src/pages/inventory/item/ItemForm.vue'

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
    const amountComputed = computed(() => Math.round((modalValue.value.rate || 0) * (modalValue.value.quantity || 0) * 100) / 100)
    const selectedItem = ref(null)

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
    const deleteRow = (index) => {
      emit('deleteRow', index)
    }
    onMounted(() => {
      if (props.usedIn === 'creditNote') modalValue.value.is_returned = true
    })
    const onAmountInput = (amount) => {
      if (amount !== (modalValue.value.rate || 0) * (modalValue.value.quantity || 1)) {
        if (!modalValue.value.quantity) modalValue.value.quantity = 1
        modalValue.value.rate = amount / modalValue.value.quantity
      }
    }
    if (props.isFifo && props.usedIn === 'sales' && !route.params.id && !props.usedInPos) {
      watch(
        () => modalValue.value.item_id,
        (newValue) => {
          if (modalValue.value.item_id) emit('onItemIdUpdate', newValue)
        },
      )
      watch(
        () => modalValue.value.quantity,
        () => {
          if (modalValue.value.item_id) emit('onItemIdUpdate')
        },
      )
    }
    const updateItem = (itemObject) => {
      if (itemObject) {
        modalValue.value.itemObj = itemObject
        modalValue.value.item_id = itemObject.id
        modalValue.value.description = itemObject.description
        modalValue.value.rate = itemObject.rate
        modalValue.value.unit_id = itemObject.unit_id
        modalValue.value.tax_scheme_id = itemObject.tax_scheme_id
        modalValue.value.selected_unit_obj = itemObject.default_unit_obj
        modalValue.value.selected_tax_scheme_obj = itemObject.default_tax_scheme_obj
      }
    }
    const choiceEndpointBaseComputed = computed(() => {
      if (props.usedIn === 'sales') return 'sales-voucher'
      if (props.usedIn === 'purchase') return 'purchase-vouchers'
      if (props.usedIn === 'creditNote') return 'credit-note'
      // if (props.usedIn === 'debitNote') return 'debit-notes'
      // if (props.usedIn === 'journal') return 'journal-entries'
    })
    return {
      ItemForm,
      expandedState,
      modalValue,
      amountComputed,
      selectedItem,
      selectedTax,
      deleteRow,
      checkPermissions,
      onAmountInput,
      choiceEndpointBaseComputed,
      updateItem,
    }
  },
}
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
              usedInPos || hasChallan ? false
              : checkPermissions('inventoryaccount.create') ? ItemForm
                : null
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
            <template v-if="isFifo && COGSData?.hasOwnProperty(index)" #append>
              <q-icon v-if="COGSData[index].totalCost.status === 'error'" color="orange" name="mdi-alert">
                <q-tooltip>
                  {{ COGSData[index].totalCost.message }}
                  <br />
                  Available Quantity {{ COGSData[index].availableStock }}
                </q-tooltip>
              </q-icon>
              <span v-else class="text-sm mt-4 text-blue-400">
                <q-tooltip>Available Stock</q-tooltip>
                {{ COGSData[index].availableStock }}
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
            <template v-if="isFifo && COGSData?.hasOwnProperty(index)" #append>
              <span v-if="COGSData[index].totalCost.status != 'error'" class="text-sm mt-4 text-blue-400">
                <q-tooltip>Cost Rate as per Fifo.</q-tooltip>
                {{ $nf(COGSData[index].totalCost / modalValue.quantity) }}
              </span>
              <!-- <q-icon v-else color="orange" name="mdi-alert">
                  <q-tooltip>
                    {{ COGSData[index].message }}
                  </q-tooltip>
                </q-icon> -->
            </template>
          </q-input>
        </div>
      </div>
      <div v-if="inputAmount" class="col-2" data-testid="amount-input">
        <!-- <span class="">{{ amountComputed }}</span> -->
        <q-input v-model="amountComputed" label="Amount" @change="onAmountInput">
          <template v-if="isFifo && COGSData?.hasOwnProperty(index) && COGSData[index].totalCost.status != 'error'" #append>
            <span class="text-sm mt-4 text-blue-400">
              <q-tooltip>Total Cost Price as per Fifo.</q-tooltip>
              {{ $nf(COGSData[index].totalCost) }}
            </span>
          </template>
        </q-input>
        <!-- <q-input v-model="amountComputed" disable label="Amount"></q-input> -->
      </div>
      <div v-else class="col-2 row justify-center items-center" data-testid="amount-input">
        <span class="">
          {{ amountComputed }}
          <span v-if="isFifo && COGSData?.hasOwnProperty(index) && COGSData[index].totalCost.status != 'error'" class="relative bg-red-200">
            <span class="text-sm ml-2 text-blue-400 absolute top-1/2 -right-0 -translate-y-1/2">
              <q-tooltip>Total Cost Price as per Fifo.</q-tooltip>
              {{ $nf(COGSData[index].totalCost) }}
            </span>
          </span>
        </span>
        <!-- <q-input v-model="amountComputed" disable label="Amount"></q-input> -->
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
        <div class="col-grow" data-testid="unit-select">
          <n-auto-complete-v2
            v-model="modalValue.unit_id"
            label="Unit"
            :emit-obj="usedInPos"
            :endpoint="`/api/company/${$route.params.company}/${choiceEndpointBaseComputed}/create-defaults/units`"
            :error="errors?.unit_id ? true : false"
            :error-message="errors?.unit_id ? errors.unit_id[0] : null"
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
        <div class="col-3" data-testid="row-tax-select">
          <n-auto-complete-v2
            v-model="modalValue.tax_scheme_id"
            label="Tax"
            :emit-obj="true"
            :endpoint="`/api/company/${$route.params.company}/${choiceEndpointBaseComputed}/create-defaults/tax_schemes`"
            :error="errors?.tax_scheme_id ? true : null"
            :error-message="errors?.tax_scheme_id ? 'This field is required' : null"
            :options="taxOptions"
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
