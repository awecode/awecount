<template>
  <q-card class="q-pa-sm">
    <q-card-section>
      <div class="row text-subtitle2 hr q-py-sm no-wrap q-col-gutter-md">
        <div class="row" :class="minimal ? 'col-7' : 'col-3'">
          {{ label }}
        </div>
        <div class="col-2 text-center">Qty</div>
        <div v-if="!minimal" class="col-2 text-center">Rate</div>
        <div class="col-2 text-center">Unit</div>
        <div class="col-2 text-center" v-if="!minimal">Amount</div>
      </div>
      <div v-for="(row, index) in modalValue" :key="row" class="row mt-1 q-col-gutter-md">
        <div :class="minimal ? 'col-7' : 'col-3'">
          <n-auto-complete-v2
            v-model="row.item_id"
            :options="itemOptions"
            :staticOption="row.selected_item_obj"
            label="Item"
            :error="
              errors?.item_id ? errors?.item_id[0]
              : rowEmpty ? 'Item is required'
              : ''
            "
            :endpoint="`v1/inventory-adjustment/create-defaults/items`"
            :emitObj="true"
            @updateObj="onItemChange"
          />
        </div>
        <div class="col-2 text-center">
          <q-input v-model.number="row.quantity" label="Quantity" type="number" data-testid="quantity-input" :error="errors && errors[index]?.quantity ? true : false" :error-message="errors && errors[index]?.quantity ? errors[index].quantity[0] : ''"></q-input>
        </div>
        <div v-if="!minimal" class="col-2 text-center">
          <q-input v-model.number="row.rate" label="Rate" type="number" data-testid="quantity-input" :error="errors && errors[index]?.rate ? true : false" :error-message="errors && errors[index]?.rate ? errors[index].rate[0] : ''"></q-input>
        </div>
        <div class="col-2">
          <n-auto-complete-v2 v-model="row.unit_id" :options="unitOptions" :staticOption="row.selected_unit_obj" label="Unit" :error="errors && errors[index]?.unit_id ? errors[index].unit_id[0] : ''" :endpoint="`v1/inventory-adjustment/create-defaults/units`" />
        </div>
        <div class="col-2 row items-center justify-center" v-if="!minimal">{{ row.rate * row.quantity }}</div>
        <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
          <q-btn v-if="!minimal" flat class="q-pa-sm focus-highLight" color="transparent" @click="() => (row.expandedState = !row.expandedState)" data-testid="expand-btn">
            <q-icon name="mdi-arrow-expand" size="20px" color="green" class="cursor-pointer" title="Expand"></q-icon>
          </q-btn>
          <q-btn flat @click="() => deleteRow(index)" class="q-pa-sm focus-highLight" color="transparent" data-testid="row-delete-btn">
            <q-icon name="delete" size="20px" color="negative" class="cursor-pointer"></q-icon>
          </q-btn>
        </div>
        <div class="col-12" v-if="row.expandedState">
          <q-input label="Description" v-model="row.description" type="textarea" class="q-mb-lg full-width" data-testid="row-description-input"></q-input>
        </div>
      </div>
      <div class="row q-mt-md">
        <div class="col-8">
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms" data-testid="add-row-btn">Add Row</q-btn>
        </div>
        <div v-if="!minimal" class="col-4 row font-medium text-gray-600">
          <div class="col-6">Total Amount</div>
          <div class="col-6">
            {{ modalValue?.reduce((accum, row) => accum + row.quantity * row.rate, 0) || 0 }}
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [
      {
        quantity: 1,
        rate: '',
        item_id: null,
        unit_id: null,
        description: '',
        expandedState: false,
      },
    ],
  },
  itemOptions: {
    type: Object,
    default: () => {
      return {
        pagination: {},
        results: [],
      }
    },
  },
  unitOptions: {
    type: Object,
    default: () => {
      return {
        pagination: {},
        results: [],
      }
    },
  },
  errors: {
    type: [Array, String, null],
    default: () => {
      return null
    },
  },
  label: {
    type: String,
    default: 'Particular(s)',
  },
  minimal: {
    type: Boolean,
    default: false,
  },
  finishedProduct: {
    type: [Number, null],
    default: null,
  },
})
const emit = defineEmits(['update:modelValue', 'deleteRow'])
const modalValue = ref(props.modelValue)
const errors = ref(props.errors)
const $q = useQuasar()
watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
  },
)
watch(
  () => props.errors,
  (newValue) => {
    errors.value = newValue
  },
)
const addRow = () => {
  modalValue.value.push({
    quantity: 1,
    rate: '',
    item_id: null,
    unit_id: null,
    description: '',
    expandedState: false,
  })
}
const deleteRow = (index) => {
  if ((props.errors && props.errors.length && props.errors[index]) || modalValue.value[index]?.id) {
    emit('deleteRow', index)
  }
  modalValue.value.splice(index, 1)
}
watch(
  () => modalValue,
  (newValue) => {
    emit('update:modelValue', newValue.value)
  },
  { deep: true },
)
const rowEmpty = computed(() => {
  let val = false
  if (props.errors && typeof props.errors === 'string') val = true
  return val
})
const onItemChange = (itemObj) => {
  if (!itemObj || !props.finishedProduct) return
  const itemIds = modalValue.value.map((item) => item.item_id)
  if (itemIds.includes(props.finishedProduct)) {
    $q.notify({
      type: 'negative',
      message: 'Item cannot be selected as both Dr and Cr',
    })
    nextTick(() => {
      modalValue.value[index].item_id = null
    })
  }
}
</script>
