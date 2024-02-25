<template>
  <q-card class="q-pa-sm">
    <q-card-section>
      <div class="row text-subtitle2 hr q-py-sm no-wrap q-col-gutter-md">
        <div class="col-5 row">
          Particular(s)
        </div>
        <div class="col-2 text-center">Qty</div>
        <div class="col-2 text-center">Rate</div>
        <div class="col-2 text-center">Amount</div>
        <div class="col-1 text-center"></div>
      </div>
      <div v-for="(row, index) in modalValue" :key="row" class="row mt-1 q-col-gutter-md">
        <div class="col-3">
          <n-auto-complete label="Item" v-model="row.item_id" :options="itemOptions" />
        </div>
        <div class="col-2 text-center">
          <q-input v-model.number="row.quantity" label="Quantity"
            :error-message="errors?.quantity ? errors.quantity[0] : null" :error="errors?.quantity ? true : false"
            type="number" data-testid="quantity-input">
          </q-input>
        </div>
        <div class="col-2 text-center">
          <q-input v-model.number="row.rate" label="Rate" :error-message="errors?.quantity ? errors.quantity[0] : null"
            :error="errors?.quantity ? true : false" type="number" data-testid="quantity-input">
          </q-input>
        </div>
        <div class="col-2">
          <q-select v-model="row.unit_id" :options="unitOptions" label="Unit" option-value="id" option-label="name"
            emit-value map-options :error-message="errors?.unit_id ? errors.unit_id[0] : null"
            :error="errors?.unit_id ? true : false" data-testid="unit-select" />
        </div>
        <div class="col-2 row items-center justify-center">{{ row.rate * row.quantity }}</div>
        <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
          <q-btn flat class="q-pa-sm focus-highLight" color="transparent"
            @click="() => (row.expandedState = !row.expandedState)" data-testid="expand-btn">
            <q-icon name="mdi-arrow-expand" size="20px" color="green" class="cursor-pointer" title="Expand"></q-icon>
          </q-btn>
          <q-btn flat @click="() => deleteRow(index)" class="q-pa-sm focus-highLight" color="transparent"
            :disable="hasChallan" data-testid="row-delete-btn">
            <q-icon name="delete" size="20px" color="negative" class="cursor-pointer"></q-icon>
          </q-btn>
        </div>
        <div class="col-12" v-if="row.expandedState">
          <q-input label="Description" v-model="row.description" type="textarea" class="q-mb-lg full-width"
            data-testid="row-description-input"></q-input>
        </div>
      </div>
      <div class="row q-mt-md">
        <div class="col-8">
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms" data-testid="add-row-btn">Add Row</q-btn>
        </div>
        <div class="col-4 row font-medium text-gray-600">
          <div class="col-6">Total Amount</div>
          <div class="col-6">
            {{ modalValue?.reduce(
              (accum, row) => accum + (row.quantity * row.rate),
              0
            ) || 0 }}
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
    default: () => [{
      quantity: 1,
      rate: '',
      item_id: null,
      unit_id: null,
      description: '',
      expandedState: false
    }]
  },
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
  errors: {
    type: Array || String,
    default: () => {
      return null
    },
  },
})
const emit = defineEmits(['update:modelValue'])
const modalValue = ref(props.modelValue)
// const rowEmpty = ref(false)
watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
  }
)
const addRow = () => {
  modalValue.value.push({
    quantity: 1,
    rate: '',
    item_id: null,
    unit_id: null,
    description: '',
    expandedState: false
  })
}
const deleteRow = (index) => {
  // if (props.errors || modalValue.value[index].id)
  //   emit(
  //     'deleteRowErr',
  //     index,
  //     modalValue.value[index]?.id ? modalValue.value[index] : null
  //   )
  modalValue.value.splice(index, 1)
}
watch(
  () => modalValue,
  (newValue) => {
    emit('update:modelValue', newValue.value)
  },
  { deep: true }
)
</script>
