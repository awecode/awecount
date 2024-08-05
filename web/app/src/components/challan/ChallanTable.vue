<template>
  <q-card-section class="overflow-y-auto -mt-4">
    <q-card class="min-w-[600px] pt-6">
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-5 row">
            Particular(s)
          </div>
          <div class="col-3 text-center">Qty</div>
          <div class="col-3 text-center">Unit</div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <div class="row q-col-gutter-md no-wrap">
            <div class="col-5">
              <n-auto-complete-v2 v-model="modalValue[index].item_id" :options="itemOptions"
                :endpoint="`v1/challan/create-defaults/items`" :staticOption="modalValue[index].selected_item_obj"
                label="Item" :error="!!errors?.[index]
                  ? errors[index].item_id
                    ? errors[index].item_id[0]
                    : rowEmpty ? 'This field is required' : ''
                  : ''
                  " :modal-component="ItemAdd" @update:modelValue="onItemChange(index)" />
            </div>
            <div class="col-3">
              <q-input v-model.number="modalValue[index].quantity" label="Quantity" type="number" :error-message="!!errors?.[index]
                ? errors[index].quantity
                  ? errors[index].quantity[0]
                  : ''
                : ''
                " :error="!!errors?.[index]
                  ? errors[index].quantity
                    ? true
                    : false
                  : false
                  "></q-input>
            </div>
            <div class="col-3">
              <n-auto-complete-v2 v-model="modalValue[index].unit_id" :options="unitOptions" label="Unit"
                :endpoint="`v1/challan/create-defaults/units`" option-value="id" option-label="name" emit-value
                map-options :error-message="!!errors?.[index]
                  ? errors[index].unit_id
                    ? 'Please Select an Option'
                    : ''
                  : ''
                  " :error="!!errors?.[index]
                    ? errors[index].unit_id
                      ? true
                      : false
                    : false
                    ">
                <template v-slot:append v-if="modalValue[index].unit_id">
                  <q-icon name="close" size="xs" @click.stop.prevent="modalValue[index].unit_id = null"
                    class="cursor-pointer" />
                </template>
              </n-auto-complete-v2>
            </div>
            <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
              <q-btn flat @click="() => removeRow(index)" class="q-pa-sm" color="transparent">
                <q-icon name="delete" size="20px" color="negative" class="cursor-pointer"></q-icon>
              </q-btn>
            </div>
          </div>
        </div>
        <div>
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms">Add Row</q-btn>
        </div>
      </div>
    </q-card>
  </q-card-section>
</template>

<script>
import ItemAdd from 'src/pages/inventory/item/ItemAdd.vue'
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
    errors: {
      type: [Array, String],
      default: () => []
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
  },
  emits: ['update:modelValue', 'deleteRow'],
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
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true }
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
      if (props.errors || props.isEdit)
        emit(
          'deleteRow',
          index,
          modalValue.value[index]?.id ? modalValue.value[index] : null
        )
      modalValue.value.splice(index, 1)
    }
    const onItemChange = (index) => {
      const itemIndex = props.itemOptions.results.findIndex((item) => item.id === modalValue.value[index].item_id)
      if (itemIndex > -1) {
        modalValue.value[index].unit_id = props.itemOptions.results[itemIndex].unit_id
      }
    }
    return {
      props,
      modalValue,
      addRow,
      removeRow,
      ItemAdd,
      // InvoiceRow,
      useCalcDiscount,
      rowEmpty,
      onItemChange
    }
  },
}
</script>
