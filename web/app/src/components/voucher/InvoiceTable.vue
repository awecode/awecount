<template>
  <q-card-section>
    <q-card>
      <div class="q-pa-lg q-col-gutter-md scroll">
        <div class="row text-subtitle2 hr q-py-sm no-wrap">
          <div class="col-4">Particular(s)</div>
          <div class="col-2 text-center">Qty</div>
          <div class="col-2 text-center">Rate</div>
          <div class="col-2 text-center">Amnt</div>
          <div class="col-2 text-center"></div>
        </div>
        <div v-for="(row, index) in modalValue" :key="index">
          <div class="row q-col-gutter-md no-wrap">
            <div class="col-4">
              <n-auto-complete v-model="modalValue[index].item_id" :options="props.itemOptions" label="Item"
                :error="errors?.party" :modal-component="ItemAdd" class="q-full-width" />
            </div>
            <div class="col-2">
              <q-input v-model.number="modalValue[index].quantity" label="Quantity" :error-message="errors"
                :error="!!errors" type="number"></q-input>
            </div>
            <div class="col-2">
              <q-input v-model.number="modalValue[index].rate" label="Rate" :error-message="errors" :error="!!errors"
                type="number"></q-input>
            </div>
            <div class="col-2">
              <q-input label="Amount" v-model="amountComputed[index]" :disable="true"></q-input>
            </div>

            <div class="col-2 row q-gutter-x-sm justify-center items-center">
              <q-icon name="mdi-arrow-expand" size="20px" color="green" class="cursor-pointer" title="Expand"
                @click="() => changeExpandedState(index)"></q-icon>
              <q-icon name="delete" size="20px" color="negative" @click="() => removeRow(index)"></q-icon>
            </div>
          </div>
          <div class="row q-col-gutter-md q-px-md" v-if="expandedState[index]">
            <div class="col-grow">
              <n-auto-complete v-model="fields" :options="props.itemOptions" label="Party" :error="errors?.party" />
            </div>
            <div class="col-2">
              <q-input v-model="fields" class="col-md-6 col-12" label="Address" :error-message="errors"
                :error="!!errors"></q-input>
            </div>
            <div class="col-2">
              <q-input v-model="fields" class="col-md-6 col-12" label="Address" :error-message="errors"
                :error="!!errors"></q-input>
            </div>
          </div>
        </div>
        <div><q-btn @click="addRow" color="green" class="q-px-lg q-py-ms">Add Row</q-btn></div>
        {{ expandedState }} --opt
      </div>
    </q-card>
  </q-card-section>
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
      }
    )
    watch(
      () => modalValue,
      (newValue) => {
        console.log('watcher invoked')
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
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
      })
      expandedState.value.push(false)
    }
    const removeRow = (index) => {
      modalValue.value.splice(index, 1)
      expandedState.value.splice(index, 1)
    }
    const changeExpandedState = (index) => {
      expandedState.value[index] = !(expandedState.value[index])
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
      changeExpandedState
    }
  },
}
</script>
