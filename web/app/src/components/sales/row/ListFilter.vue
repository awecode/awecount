<template>
  <div>
    <div class="q-mx-lg q-mt-md">
      <h6 class="q-ma-none font-weight-bold text-grey-9">Filters</h6>
    </div>
    <hr />
    <div class="q-ma-md">
      <div class="row q-col-gutter-md">
        <q-input class="col-6 col-md-12" label="From Date"> </q-input>
        <q-input class="col-6 col-md-12" label="To Date"> </q-input>
      </div>
      <q-select
        label="Sales Agent"
        :options="fetchedOptions[`sales-agent`]"
        option-value="id"
        option-label="name"
        map-options
        emit-value
      />
      <q-select
        label="Party"
        :options="fetchedOptions.parties"
        option-value="id"
        option-label="name"
        map-options
        emit-value
      />
      <q-select
        label="Tax Scheme"
        :options="fetchedOptions.tax_scheme"
        option-value="id"
        option-label="name"
        map-options
        emit-value
      />
      <q-select
        label="Item Category"
        :options="fetchedOptions[`inventory-categories`]"
        option-value="id"
        option-label="name"
        map-options
        emit-value
      />
      <q-select
        label="Items"
        :options="fetchedOptions.item_choices"
        option-value="id"
        option-label="name"
        map-options
        emit-value
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Ref } from 'vue'
import useApi from 'src/composables/useApi'
export default {
  props: {
    label: {
      type: String,
      default: 'Select',
    },
    modelValue: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalValue = ref(props.modelValue)
    const fetchedOptions: Ref<Record<string, Array<object> | null>> = ref({
      'sales-agent': null,
      parties: null,
      tax_scheme: null,
      'inventory-categories': null,
      item_choices: null,
    })
    const usedOptions: Array<string> = [
      'sales-agent',
      'parties',
      'tax_scheme',
      'inventory-categories',
    ]
    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
      }
    )
    const filterParamsComputed = computed(() => {
      return 0
    })
    return { filterParamsComputed, usedOptions, fetchedOptions }
  },
  created() {
    this.usedOptions.forEach((type) => {
      useApi(`/v1/${type}/choices/`).then((data) => {
        this.fetchedOptions[type] = data
      })
      useApi('/v1/items/sales-choices/').then((data) => {
        this.fetchedOptions.item_choices = data
      })
    })
  },
}
</script>
