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
          <div class="col-3 text-center">Qty</div>
          <div class="col-3 text-center">Unit</div>
          <div class="col-1 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <!-- <InvoiceRow
            v-if="modalValue[index]"
            :usedIn="props.usedIn"
            v-model="modalValue[index]"
            :itemOptions="itemOptions"
            :unitOptions="unitOptions"
            :taxOptions="taxOptions"
            :discountOptions="discountOptions"
            :index="index"
            :rowEmpty="(rowEmpty && index === 0) || false"
            @deleteRow="(index) => removeRow(index)"
            :errors="
              !rowEmpty ? (Array.isArray(errors) ? errors[index] : null) : null
            "
          /> -->
          <div class="row q-col-gutter-md no-wrap">
            <div class="col-5">
              <n-auto-complete
                v-model="modalValue[index].item_id"
                :options="itemOptions"
                label="Item"
                :error="
                  !!errors?.[index]
                    ? errors[index].item_id
                      ? errors[index].item_id[0]
                      : rowEmpty || false
                    : false
                "
                :modal-component="ItemAdd"
              />
            </div>
            <div class="col-3">
              <q-input
                v-model.number="modalValue[index].quantity"
                label="Quantity"
                type="number"
                :error-message="
                  !!errors?.[index]
                    ? errors[index].quantity
                      ? errors[index].quantity[0]
                      : false
                    : false
                "
                :error="
                  !!errors?.[index]
                    ? errors[index].quantity
                      ? true
                      : false
                    : false
                "
              ></q-input>
            </div>
            <div class="col-3">
              <q-select
                v-model="modalValue[index].unit_id"
                :options="unitOptions"
                label="Unit"
                option-value="id"
                option-label="name"
                emit-value
                map-options
                :error-message="
                  !!errors?.[index]
                    ? errors[index].unit_id
                      ? 'Please Select an Option'
                      : false
                    : false
                "
                :error="
                  !!errors?.[index]
                    ? errors[index].unit_id
                      ? true
                      : false
                    : false
                "
              >
                <template v-slot:append v-if="modalValue[index].unit_id">
                  <q-icon
                    name="close"
                    size="xs"
                    @click.stop.prevent="modalValue[index].unit_id = null"
                    class="cursor-pointer"
                  />
                </template>
              </q-select>
            </div>
            <div
              class="col-1 row no-wrap q-gutter-x-sm justify-center items-center"
            >
              <q-btn
                flat
                @click="() => removeRow(index)"
                class="q-pa-sm"
                color="transparent"
              >
                <q-icon
                  name="delete"
                  size="20px"
                  color="negative"
                  class="cursor-pointer"
                ></q-icon>
              </q-btn>
            </div>
          </div>
        </div>
        <div>
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms"
            >Add Row</q-btn
          >
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
      type: Array || String,
      default: () => {
        return null
      },
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
      debugger
      if (props.errors || props.isEdit)
        emit(
          'deleteRow',
          index,
          modalValue.value[index]?.id ? modalValue.value[index] : null
        )
      modalValue.value.splice(index, 1)
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
    }
  },
}
</script>
