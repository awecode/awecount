<template>
  <q-card class="q-pa-sm">
    <q-card-section>
      <div class="row text-subtitle2 hr q-py-sm no-wrap q-col-gutter-md">
        <div class="row" :class="props.type === 'Cr' ? 'col-7' : 'col-3'">
          {{ label }}
        </div>
        <div class="col-2 text-center">Qty</div>
        <div v-if="props.type === 'Dr'" class="col-2 text-center">Rate</div>
        <div class="col-2 text-center">Unit</div>
        <div class="col-2 text-center" v-if="props.type === 'Dr'">Amount</div>
      </div>
      <div v-for="(row, index) in modalValue" :key="row" class="row mt-1 q-col-gutter-md">
        <template v-if="row.transaction_type === props.type">
          <div :class="props.type === 'Cr' ? 'col-7' : 'col-3'">
            <n-auto-complete label="Item" v-model="row.item_id" :options="itemOptions"
              @update:model-value="onItemChange(index)"
              :error="rowEmpty ? 'This field is required.' : errors && errors[index]?.item_id ? errors[index].item_id[0] : null" />
          </div>
          <div class="col-2 text-center">
            <q-input v-model.number="row.quantity" label="Quantity" type="number" data-testid="quantity-input"
              :error="errors && errors[index]?.quantity ? true : false"
              :error-message="errors && errors[index]?.quantity ? errors[index].quantity[0] : ''">
            </q-input>
          </div>
          <div v-if="props.type === 'Dr'" class="col-2 text-center">
            <q-input v-model.number="row.rate" label="Rate" data-testid="quantity-input"
              :error="errors && errors[index]?.rate ? true : false"
              :error-message="errors && errors[index]?.rate ? errors[index].rate[0] : ''">
            </q-input>
          </div>
          <div class="col-2">
            <q-select v-model="row.unit_id" :options="unitOptions" label="Unit" option-value="id" option-label="name"
              emit-value map-options data-testid="unit-select" :error="errors && errors[index]?.unit_id ? true : false"
              :error-message="errors && errors[index]?.unit_id ? errors[index].unit_id[0] : ''" />
          </div>
          <div class="col-2 row items-center justify-center" v-if="props.type === 'Dr'">{{ row.rate * row.quantity }}
          </div>
          <div class="col-1 row no-wrap q-gutter-x-sm justify-center items-center">
            <q-btn flat @click="() => deleteRow(index)" class="q-pa-sm focus-highLight" color="transparent"
              data-testid="row-delete-btn">
              <q-icon name="delete" size="20px" color="negative" class="cursor-pointer"></q-icon>
            </q-btn>
          </div>
        </template>
      </div>
      <div class="row q-mt-md">
        <div class="col-8">
          <q-btn @click="addRow" color="green" outline class="q-px-lg q-py-ms" data-testid="add-row-btn">Add Row</q-btn>
        </div>
        <div v-if="props.type === 'Dr'" class="col-4 row font-medium text-gray-600">
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
  type: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Array,
    default: () => [{
      quantity: 1,
      item_id: null,
      unit_id: null,
      transaction_type: 'Cr'
    },
    {
      quantity: 1,
      rate: 0,
      item_id: null,
      unit_id: null,
      transaction_type: 'Dr'
    }
    ]
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
      return []
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
})
const emit = defineEmits(['update:modelValue', 'deleteRow'])
const modalValue = ref(props.modelValue)
const errors = ref(props.errors)
const $q = useQuasar()
watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
  }
)
watch(
  () => props.errors,
  (newValue) => {
    errors.value = newValue
  }
)
const addRow = () => {
  let newRow = {
    quantity: 1,
    item_id: null,
    unit_id: null,
    transaction_type: props.type
  }
  if (props.transaction_type === 'Dr') newRow.rate = 0
  modalValue.value.push(newRow)
}
const deleteRow = (index) => {
  if (props.errors && props.errors.length && props.errors[index] || modalValue.value[index]?.id) {
    emit('deleteRow', index)
  }
  modalValue.value.splice(index, 1)
}
watch(
  () => modalValue,
  (newValue) => {
    emit('update:modelValue', newValue.value)
  },
  { deep: true }
)
const rowEmpty = computed(() => {
  let val = false
  if (props.errors && typeof props.errors === 'string') val = true
  return val
})

const onItemChange = (index) => {
  if (!modalValue.value || !modalValue.value.length) return
  const drIds = []
  const crIds = []
  modalValue.value.forEach((row) => {
    if (row.transaction_type === 'Dr') {
      drIds.push(row.item_id)
    } else crIds.push(row.item_id)
  })

  const itemIds = drIds.concat(crIds)
  const itemIdSet = new Set(itemIds)
  if (itemIds.length > itemIdSet.size) {
    $q.notify({
      type: 'negative',
      message: 'Item cannot be selected as both Dr and Cr'
    })
    nextTick(() => {
      modalValue.value[index].item_id = null
    })
  }
}
</script>
