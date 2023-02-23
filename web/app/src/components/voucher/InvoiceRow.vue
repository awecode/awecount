<template>
  <div>
    <div class="row q-col-gutter-md no-wrap">
      <div class="col-5">
        <n-auto-complete v-model="selectedItem" :options="itemOptions" label="Item" :error="errors?.party"
          :modal-component="ItemAdd" class="q-full-width" />
      </div>
      <div class="col-2">
        <q-input v-model.number="modalValue.quantity" label="Quantity" :error-message="errors" :error="!!errors"
          type="number"></q-input>
      </div>
      <div class="col-2">
        <q-input v-model.number="modalValue.rate" label="Rate" :error-message="errors" :error="!!errors"
          type="number"></q-input>
      </div>
      <div class="col-2 full-height row">
        <q-input v-model="amountComputed" disable label="Amount"></q-input>
      </div>
      <div class="col-1 row q-gutter-x-sm justify-center items-center">
        <q-icon name="mdi-arrow-expand" size="20px" color="green" itemObj class="cursor-pointer" title="Expand"
          @click="() => (expandedState = !expandedState)"></q-icon>
        <q-icon name="delete" size="20px" color="negative" @click="() => deleteRow(index)"
          class="cursor-pointer"></q-icon>
      </div>
    </div>
    <div class="row q-col-gutter-md q-px-lg" v-if="expandedState">
      <div class="col-grow">
        <q-select v-model="modalValue.unit_id" :options="unitOptions" label="Unit" option-value="id" option-label="name"
          map-options />
      </div>
      <div class="col-md-4 row q-col-gutter-md">
        <div class="col-grow">
          <n-auto-complete v-model="modalValue.discount_type" label="Discount*" :options="discountOptions">
          </n-auto-complete>
        </div>
        <div class="col-3" v-if="
          modalValue.discount_type === 'Amount' ||
          modalValue.discount_type === 'Percent'
        ">
          <q-input v-model.number="modalValue.discount" label="Discount"></q-input>
        </div>
      </div>
      <!-- <div class="col-3">
                            <div class="row bg-red-1">
                              <n-auto-complete
                                class="col-grow col-12"
                                v-model="modalValue[index].discount_type"
                                label="Discount*"
                                :error="errors?.discount_types"
                                :options="discountOptions"
                              ></n-auto-complete>
                              <div
                                class="col-4"
                                v-if="
                                  modalValue[index].discount_type === 'Amount' ||
                                  modalValue[index].discount_type === 'Percent'
                                "
                              >
                                <q-input
                                  class="col-12"
                                  v-model="modalValue.discount"
                                  label="Discount"
                                ></q-input>
                              </div>
                            </div>
                          </div> -->
      <div class="col-3">
        <q-select v-model="selectedTax" :options="taxOptions" label="Tax" option-value="id" option-label="name"
          map-options />
      </div>
    </div>
  </div>
</template>

<script>
import ItemAdd from 'src/pages/inventory/item/ItemAdd.vue'
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
      type: Object,
      default: () => {
        return {
          discount: '',
          quantity: '',
          rate: '',
          item_id: '',
          unit_id: '',
          description: '',
          discount: '',
          discount_type: null,
          itemObj: null,
          tax_scheme_id: '',
          taxObj: null,
          discount_id: null,
          itemObj: null,
        }
      },
    },
    index: {
      type: Number,
      default: () => null
    },
  },
  emits: ['update:modelValue', 'deleteRow'],
  setup(props, { emit }) {
    const expandedState = ref(false)
    const modalValue = ref(props.modelValue)
    const selectedTax = ref(null)
    const amountComputed = computed(
      () => (modalValue.value.rate || 0) * (modalValue.value.quantity || 0)
    )
    const selectedItem = ref(null)
    watch(
      () => props.modelValueProps,
      (newValue) => {
        modalValue.value = newValue
      }
    )
    watch(
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
    watch(selectedItem, (newValue) => {
      const index = props.itemOptions.findIndex((item) => item.id === newValue)
      const discountobject = props.itemOptions[index]
      modalValue.value.itemObj = discountobject
      modalValue.value.item_id = discountobject.id
    })
    watch(selectedTax, (newValue) => {
      modalValue.value.taxObj = newValue
      modalValue.value.tax_scheme_id = newValue.id
    })
    const deleteRow = (index) => {
      debugger
      emit('deleteRow', index)
    }
    return {
      ItemAdd,
      expandedState,
      modalValue,
      amountComputed,
      selectedItem,
      selectedTax,
      deleteRow
    }
  },
}
</script>
