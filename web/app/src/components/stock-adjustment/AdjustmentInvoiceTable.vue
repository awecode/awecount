
import { Script } from 'vm';
<template>
  <q-card class="q-py-md">
    <q-card-section>
      <div class="row text-subtitle2 hr q-py-sm no-wrap" :class="usedInPos ? 'mb-2' : ''">
        <div class="col-5 row">
          <div :class="usedIn === 'creditNote' ? 'col-10' : 'col-12'">
            Particular(s)
          </div>
          <div v-if="usedIn === 'creditNote'" class="col-2 text-center">
            Return
          </div>
        </div>
        <div class="col-2 text-center">Qty</div>
        <div class="col-2 text-center">Rate</div>
        <div class="col-2 text-center">Amount</div>
        <div class="col-1 text-center"></div>
      </div>
      <div v-for="row in modalValue" :key="row">
        <n-auto-complete label="Item" v-model="fields.item" :options="formDefaults.collections?.items"
          :error="errors.item" />
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
      description: ''
    }]
  }
})
</script>
