<script>
import useCalcDiscount from 'src/composables/useCalcDiscount.js'
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
    errors: {
      type: [Array, String],
      default: () => [],
    },
    modelValue: {
      type: Array,
      default: () => [
        {
          quantity: 1,
          rate: 0,
          item_id: null,
          unit_id: '',
        },
      ],
    },
    isEdit: {
      type: Boolean,
      default: () => false,
    },
    usedIn: {
      type: String,
      default: 'challan',
    },
  },
  emits: ['update:modelValue', 'deleteRow'],
  setup(props, { emit }) {
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
    const addRow = () => {
      modalValue.value.push({
        quantity: 1,
        rate: 0,
        item_id: null,
        unit_id: '',
      })
    }
    const removeRow = (index) => {
      if (props.errors || props.isEdit) emit('deleteRow', index, modalValue.value[index]?.id ? modalValue.value[index] : null)
      modalValue.value.splice(index, 1)
    }
    const onItemChange = (index) => {
      const itemIndex = props.itemOptions.results.findIndex(item => item.id === modalValue.value[index].item_id)
      if (itemIndex > -1) {
        modalValue.value[index].unit_id = props.itemOptions.results[itemIndex].unit_id
        modalValue.value[index].selected_unit_obj = props.itemOptions.results[itemIndex].default_unit_obj
      }
    }
    const choiceEndpointBaseComputed = computed(() => {
      if (props.usedIn === 'challan') return 'challan'
      if (props.usedIn === 'purchase-order') return 'purchase-order'
    })
    return {
      props,
      modalValue,
      addRow,
      removeRow,
      ItemAdd,
      // InvoiceRow,
      useCalcDiscount,
      rowEmpty,
      onItemChange,
      choiceEndpointBaseComputed,
    }
  },
}
</script>

<template>
  <q-card-section class="overflow-y-auto -mt-4">
    <q-card class="min-w-[600px] pt-6">
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-5 row">
            Particular(s)
          </div>
          <div class="col-3 text-center">
            Qty
          </div>
          <div class="col-3 text-center">
            Unit
          </div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <div class="row q-col-gutter-md no-wrap">
            <div class="col-5">
              <n-auto-complete-v2
                v-model="modalValue[index].item_id"
                label="Item"
                :endpoint="`v1/${choiceEndpointBaseComputed}/create-defaults/items`"
                :error="
                  !!errors?.[index]
                    ? errors[index].item_id ? errors[index].item_id[0]
                      : rowEmpty ? 'This field is required'
                        : ''
                    : ''
                "
                :modal-component="ItemAdd"
                :options="itemOptions"
                :static-option="modalValue[index].selected_item_obj"
                @update:model-value="onItemChange(index)"
              />
            </div>
            <div class="col-3">
              <q-input
                v-model.number="modalValue[index].quantity"
                label="Quantity"
                type="number"
                :error="
                  !!errors?.[index]
                    ? errors[index].quantity
                      ? true
                      : false
                    : false
                "
                :error-message="
                  !!errors?.[index]
                    ? errors[index].quantity
                      ? errors[index].quantity[0]
                      : ''
                    : ''
                "
              />
            </div>
            <div class="col-3">
              <n-auto-complete-v2
                v-model="modalValue[index].unit_id"
                emit-value
                map-options
                label="Unit"
                option-label="name"
                option-value="id"
                :endpoint="`v1/${choiceEndpointBaseComputed}/create-defaults/units`"
                :error="
                  !!errors?.[index]
                    ? errors[index].unit_id
                      ? true
                      : false
                    : false
                "
                :error-message="
                  !!errors?.[index]
                    ? errors[index].unit_id
                      ? 'Please Select an Option'
                      : ''
                    : ''
                "
                :options="unitOptions"
                :static-option="modalValue[index].selected_unit_obj"
              >
                <template v-if="modalValue[index].unit_id" #append>
                  <q-icon
                    class="cursor-pointer"
                    name="close"
                    size="xs"
                    @click.stop.prevent="modalValue[index].unit_id = null"
                  />
                </template>
              </n-auto-complete-v2>
            </div>
            <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
              <q-btn
                flat
                class="q-pa-sm"
                color="transparent"
                @click="() => removeRow(index)"
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
        </div>
        <div>
          <q-btn
            outline
            class="q-px-lg q-py-ms"
            color="green"
            @click="addRow"
          >
            Add Row
          </q-btn>
        </div>
      </div>
    </q-card>
  </q-card-section>
</template>
