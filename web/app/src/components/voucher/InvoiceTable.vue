<template>
  <q-card-section>
    <q-card>
      <div class="q-pa-lg q-col-gutter-md">
        <div class="row text-subtitle2 hr q-py-sm">
          <div class="col-grow">Particular(s)</div>
          <div class="col-2 text-center">Qty</div>
          <div class="col-2 text-center">Rate</div>
          <div class="col-2 text-center">Amnt</div>
          <div class="col-2 text-center"></div>
        </div>
        <div v-for="(row, index) in rows" :key="index">
          <div class="row q-col-gutter-md">
            <div class="col-grow">
              <n-auto-complete v-model="fields" :options="props.itemOptions" label="Party" :error="errors?.party"
                :modal-component="PartyForm" />
            </div>
            <div class="col-2">
              <q-input v-model="fields" class="col-md-6 col-12" label="Address" :error-message="errors"
                :error="!!errors"></q-input>
            </div>
            <div class="col-2">
              <q-input v-model="fields" class="col-md-6 col-12" label="Address" :error-message="errors"
                :error="!!errors"></q-input>
            </div>
            <div class="col-2">asas</div>
            <div class="col-2">asas</div>
          </div>
          <div class="row q-col-gutter-md q-md-px-xl">
            <div class="col-grow">
              <n-auto-complete v-model="fields" :options="props.itemOptions" label="Party" :error="errors?.party"
                :modal-component="PartyForm" />
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
        {{ props.itemOptions }} --opt
      </div>
    </q-card>
  </q-card-section>
</template>

<script>
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  props: {
    itemOptions: {
      type: Object,
      default: () => { return {} },
    },
    modelValue: {
      type: Array,
      default: () => [{
        discount: '',
        quantity: '',
        rate: '',
        item_id: '',
        unit_id: '',
        description: '',
        discount: '',
        discount_type: null,
        tax_scheme_id: ''
      }]
    }
  },

  setup(props, context) {
    const rows = ref(1)
    return {
      rows,
      props
    }
  },
}
</script>
