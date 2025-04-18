<script lang="ts">
import type { Ref } from 'vue'
import DateConverter from '@/components/date/VikramSamvat.js'
import { modes } from '@/helpers/constants/invoice'
import { useLoginStore } from '@/stores/login-info'

export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
    changeModes: {
      type: Boolean,
      default: () => {
        return false
      },
    },
    modeOptions: {
      type: Array,
      default: () => {
        return []
      },
    },
    modelValue: {
      type: [Object, String, Number],
      default: () => null,
    },
  },
  emits: ['updateMode'],
  setup(props, { emit }) {
    const route = useRoute()
    const modesValue: Ref<number | null> = ref(props.fields?.mode)
    const $q = useQuasar()
    const store = useLoginStore()
    watch(
      () => props.fields?.mode,
      (newValue) => {
        modesValue.value = newValue
      },
    )
    const dateComputed = computed(() => {
      return DateConverter.getRepresentation(props.fields?.date, store.isCalendarInAD ? 'ad' : 'bs')
    })
    const modeComputed: Ref<string> = computed(() => {
      if (typeof props.fields?.mode === 'number') {
        const index: number = props.modeOptions.findIndex(item => item.id === props.fields?.mode)
        return props.modeOptions[index].name
      } else {
        return props.fields?.mode
      }
    })
    const discountComputed = computed(() => {
      if (props.fields?.discount_obj) {
        return `${props.fields.discount_obj.value}` + ' ' + `${props.fields.discount_obj.type === 'Amount' ? '-/' : '%'}`
      } else if (props.fields?.discount) {
        return `${props.fields.discount}` + ' ' + `${props.fields.discount_type === 'Amount' ? '-/' : '%'}`
      } else {
        return false
      }
    })
    const submitChangeModes = (id: number) => {
      const endpoint = `/api/company/${route.params.company}/sales-voucher/${id}/update-mode/`
      const body: object = { method: 'POST', body: { mode: modesValue.value } }
      useApi(endpoint, body)
        .then(() => {
          emit('updateMode', modesValue.value)
          isChangeOpen.value = false
          $q.notify({
            color: 'positive',
            message: 'Mode Updated!',
            icon: 'check_circle',
          })
        })
        .catch(err => console.log('err from the api', err))
    }
    const isChangeOpen: Ref<boolean> = ref(false)
    return {
      props,
      discountComputed,
      isChangeOpen,
      modesValue,
      modes,
      submitChangeModes,
      modeComputed,
      dateComputed,
    }
  },
}
</script>

<template>
  <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
    <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
      <template v-if="fields?.party_name">
        <div class="col-12 col-md-6 row">
          <div class="col-6">
            Party
          </div>
          <div class="col-6">
            {{ fields?.party_name }}
          </div>
        </div>
        <div v-if="fields?.customer_name" class="col-12 col-md-6 row">
          <div class="col-6">
            Name on Invoice
          </div>
          <div class="col-6">
            {{ fields?.customer_name }}
          </div>
        </div>
      </template>
      <div v-else class="col-12 col-md-6 row">
        <div class="col-6">
          {{ fields?.customer_name ? 'Customer' : '' }}
        </div>
        <div class="col-6">
          {{ fields?.customer_name || '' }}
        </div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">
          Address
        </div>
        <div class="col-6">
          {{ fields?.address }}
        </div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">
          Status
        </div>
        <div class="col-6">
          {{ fields?.status }}
        </div>
      </div>
      <div v-if="fields?.discount_type || fields?.discount_obj" class="col-12 col-md-6 row">
        <div class="col-6">
          Discount
        </div>
        <div class="col-6">
          <template v-if="fields?.discount_obj">
            <FormattedNumber v-if="fields?.discount_obj.type === 'Amount'" type="currency" :value="fields?.discount_obj.value" />
            <FormattedNumber
              v-else-if="fields?.discount_obj.type === 'Percent'"
              type="unit"
              unit="percent"
              :value="fields?.discount_obj.value"
            />
          </template>
          <template v-else-if="fields?.discount_type">
            <FormattedNumber v-if="fields?.discount_type === 'Amount'" type="currency" :value="fields?.discount" />
            <FormattedNumber
              v-else-if="fields?.discount_type === 'Percent'"
              type="unit"
              unit="percent"
              :value="fields?.discount"
            />
          </template>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6 q-gutter-y-lg">
      <div class="col-12 col-md-6 row">
        <div class="col-6">
          Date
        </div>
        <div class="col-6">
          {{ dateComputed }}
        </div>
      </div>
      <div v-if="changeModes" class="col-12 col-md-6 row">
        <div class="col-6">
          Mode
        </div>
        <div class="col-6">
          <span class="q-mr-sm">{{ modeComputed }}</span>
          <q-btn icon="edit" size="sm" @click="() => (isChangeOpen = true)" />
        </div>
      </div>
      <div v-else class="col-12 col-md-6 row">
        <div class="col-6">
          Mode
        </div>
        <div class="col-6">
          {{ fields?.mode }}
        </div>
      </div>
      <div v-if="fields.mode === 'Bank Deposit'" class="col-12 col-md-6 row">
        <div class="col-6">
          Bank Account
        </div>
        <div class="col-6">
          {{ fields?.bank_account_name }}
        </div>
      </div>
      <div v-if="fields.challan_numbers && fields.challan_numbers.length > 0" class="col-12 col-md-6 row">
        <div class="col-6">
          Challan Voucher No.
        </div>
        <div class="col-6">
          {{ fields.challan_numbers.join(',') }}
        </div>
      </div>
    </div>
    <q-dialog v-model="isChangeOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-grey-4">
          <div class="text-h6 flex justify-between">
            <span class="q-mx-md">Edit Mode</span>
            <q-btn
              v-close-popup
              dense
              flat
              round
              class="text-white bg-red-500"
              icon="close"
            />
          </div>
        </q-card-section>
        <q-card-section class="q-mx-md">
          <div class="text-right q-mt-lg row justify-between q-mx-lg">
            <q-select
              v-model="modesValue"
              emit-value
              map-options
              class="col-12"
              label="Mode"
              option-label="name"
              option-value="id"
              :options="props.modeOptions.length > 0 ? modes.concat(props.modeOptions) : modes"
            />
          </div>
          <div class="row q-mt-lg justify-end">
            <q-btn
              class="q-mt-md"
              color="orange-5"
              label="update"
              @click="() => submitChangeModes(props.fields.id)"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-card>
</template>
