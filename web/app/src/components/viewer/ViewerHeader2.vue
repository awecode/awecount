<template>
  <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
    <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
      <template v-if="fields?.party_name">
        <div class="col-12 col-md-6 row">
          <div class="col-6">Party</div>
          <div class="col-6">
            {{ fields?.party_name }}
          </div>
        </div>
        <div v-if="fields?.customer_name" class="col-12 col-md-6 row">
          <div class="col-6">Name on Invoice</div>
          <div class="col-6">
            {{ fields?.customer_name }}
          </div>
        </div>
      </template>
      <div v-else class="col-12 col-md-6 row">
        <div class="col-6">{{ fields?.customer_name ? 'Customer' : '' }}</div>
        <div class="col-6">{{ fields?.customer_name || '' }}</div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">Address</div>
        <div class="col-6">{{ fields?.address }}</div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">Status</div>
        <div class="col-6">{{ fields?.status }}</div>
      </div>
      <div class="col-12 col-md-6 row" v-if="discountComputed">
        <div class="col-6">Discount</div>
        <div class="col-6">
          {{ discountComputed }}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6 q-gutter-y-lg">
      <div class="col-12 col-md-6 row">
        <div class="col-6">Date</div>
        <div class="col-6">{{ dateComputed }}</div>
      </div>
      <div v-if="changeModes" class="col-12 col-md-6 row">
        <div class="col-6">Payment Mode</div>
        <div class="col-6">
          <span class="q-mr-sm">{{ paymentModeComputed }}</span>
          <q-btn @click="() => (isChangeOpen = true)" icon="edit" size="sm"></q-btn>
        </div>
      </div>
      <div v-else class="col-12 col-md-6 row">
        <div class="col-6">Payment Mode</div>
        <div class="col-6">
          {{ fields?.payment_mode ?? 'Credit' }}
        </div>
      </div>
      <div v-if="fields.challan_numbers && fields.challan_numbers.length > 0" class="col-12 col-md-6 row">
        <div class="col-6">Challan Voucher No.</div>
        <div class="col-6">
          {{ fields.challan_numbers.join(',') }}
        </div>
      </div>
    </div>
    <q-dialog v-model="isChangeOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-grey-4">
          <div class="text-h6 flex justify-between">
            <span class="q-mx-md">Edit Payment Mode</span>
            <q-btn icon="close" class="text-white bg-red-500" flat round dense v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class="q-mx-md">
          <div class="text-right q-mt-lg row justify-between q-mx-lg">
            <q-select v-model="paymentModeValue" label="Payment Mode" class="col-12" :options="[{ id: null, name: 'Credit' }, ...props.paymentModeOptions]" option-value="id" option-label="name" map-options emit-value></q-select>
          </div>
          <div class="row q-mt-lg justify-end">
            <q-btn label="update" color="orange-5" class="q-mt-md" @click="() => submitChangeModes(props.fields.id)"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-card>
</template>

<script lang="ts">
import { Ref } from 'vue'
import { modes } from 'src/helpers/constants/invoice'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
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
    paymentModeOptions: {
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
    const paymentModeValue: Ref<number | null> = ref(props.fields?.payment_mode)
    const $q = useQuasar()
    const store = useLoginStore()
    watch(
      () => props.fields?.payment_mode,
      (newValue) => {
        paymentModeValue.value = newValue
      },
    )
    const dateComputed = computed(() => {
      return DateConverter.getRepresentation(props.fields?.date, store.isCalendarInAD ? 'ad' : 'bs')
    })
    const paymentModeComputed: Ref<string> = computed(() => {
      if (typeof props.fields?.payment_mode === 'number') {
        const index: number = props.paymentModeOptions.findIndex((item) => item.id === props.fields?.payment_mode)
        return props.paymentModeOptions[index].name
      } else if (props.fields?.payment_mode === null) {
        return 'Credit'
      } else return props.fields?.payment_mode
    })
    const discountComputed = computed(() => {
      if (props.fields?.discount_obj) {
        return `${props.fields.discount_obj.value}` + ' ' + `${props.fields.discount_obj.type === 'Amount' ? '-/' : '%'}`
      } else if (props.fields?.discount) {
        return `${props.fields.discount}` + ' ' + `${props.fields.discount_type === 'Amount' ? '-/' : '%'}`
      } else return false
    })
    const submitChangeModes = (id: number) => {
      const endpoint = `v1/sales-voucher/${id}/update-payment-mode/`
      const body: object = { method: 'POST', body: { payment_mode: paymentModeValue.value } }
      useApi(endpoint, body)
        .then(() => {
          emit('updateMode', paymentModeValue.value)
          isChangeOpen.value = false
          $q.notify({
            color: 'positive',
            message: 'Payment Mode Updated!',
            icon: 'check_circle',
          })
        })
        .catch((err) => console.log('err from the api', err))
    }
    const isChangeOpen: Ref<boolean> = ref(false)
    return {
      props,
      discountComputed,
      isChangeOpen,
      paymentModeValue,
      modes,
      submitChangeModes,
      paymentModeComputed,
      dateComputed,
    }
  },
}
</script>
