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
      <div class="q-my-md">
        <div class="text-grey-8 text-subtitle2">
          <strong>Statuses :</strong>
        </div>
        <div class="row q-gutter-sm q-pt-md">
          <q-btn
            @click="() => onStatusClick(statuses)"
            style="border-radius: 1rem"
            class="q-py-sm q-px-md"
            v-for="(statuses, index) in statusesChoice"
            :key="index"
            :class="
              activeStatuses.includes(statuses)
                ? 'bg-blue-1 text-blue-9'
                : 'bg-grey-4 text-grey-9'
            "
          >
            <!-- TODO: add animation -->
            <q-icon
              v-if="activeStatuses.includes(statuses)"
              name="check"
              size="sm"
              color="blue"
              class="q-mr-xs"
            ></q-icon>
            <span>
              {{ statuses }}
            </span>
          </q-btn>
        </div>
        <div class="q-mt-md row q-gutter-x-md">
          <q-btn color="green" label="Filter" @click="onFilterClick"></q-btn>
          <q-btn color="red" icon="close"></q-btn>
        </div>
      </div>
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
    // modelValue: {
    //   type: Object,
    //   default: () => {
    //     return {}
    //   },
    // },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    // const modalValue = ref(props.modelValue)
    const fetchedOptions: Ref<Record<string, Array<object> | null>> = ref({
      'sales-agent': null,
      parties: null,
      tax_scheme: null,
      'inventory-categories': null,
      item_choices: null,
    })
    const statusesChoice = [
      'Draft',
      'Issued',
      'Paid',
      'Partially Paid',
      'Cancelled',
    ]
    const activeStatuses: Ref<Array<string>> = ref([])
    const usedOptions: Array<string> = [
      'sales-agent',
      'parties',
      'tax_scheme',
      'inventory-categories',
    ]
    const onStatusClick = (status: string) => {
      const index: number = activeStatuses.value.findIndex(
        (item) => item === status
      )
      if (index >= 0) {
        activeStatuses.value.splice(index, 1)
      } else {
        activeStatuses.value.push(status)
      }
      console.log(activeStatuses.value)
    }
    const onFilterClick = () => {}
    // watch(
    //   () => props.modelValue,
    //   (newValue) => {
    //     modalValue.value = newValue
    //   }
    // )
    const filterParamsComputed = computed(() => {
      return 0
    })
    onMounted(() => console.log('params'))
    return {
      filterParamsComputed,
      usedOptions,
      fetchedOptions,
      statusesChoice,
      activeStatuses,
      onStatusClick,
      onFilterClick,
    }
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
  // onmounted() {
  //   console.log(this.$route.params, 'params')
  // },
}
</script>
