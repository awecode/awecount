<script setup>
import checkPermissions from '@/composables/checkPermissions'
import LedgerForm from '@/components/views/account/ledger/LedgerForm.vue'

const props = defineProps(['voucher', 'index', 'options', 'errors'])
const emit = defineEmits(['deleteVoucher', 'checkAddVoucher'])
const voucher = ref(props.voucher)
const openDescription = ref(false)
watch(
  () => props.voucher,
  newValue => (voucher.value = newValue),
)
// watch(voucher.value, (a) => {
//   a.type == 'Dr' ? (a.cr_amount = null) : (a.dr_amount = null)
//   emit('updateVoucher', a, props.index)
// })

// const errors = ref(props?.errors)
// watch(() => props.errors, (a) => {
//   console.log(props.errors[0])
//   errors.value = props.errors
//   console.log(errors.value)
// })

const deleteVoucher = () => {
  emit('deleteVoucher', props.index)
}
const focusOut = () => {
  emit('checkAddVoucher', props.index)
}
const onSwitchDrCr = (mode) => {
  if (mode === 'Cr') {
    voucher.value.dr_amount = null
  } else if (mode === 'Dr') {
    voucher.value.cr_amount = null
  }
}
</script>

<template>
  <div>
    <hr />
    <div class="row no-wrap q-gutter-x-md q-py-sm items-center">
      <div class="q-mr-lg text-center" style="flex-grow: 0; flex-shrink: 0">
        {{ props.index + 1 }}
      </div>
      <div class="row q-col-gutter-md" style="flex-grow: 1">
        <div class="col-2">
          <!-- <n-auto-complete v-model="voucher.type" :options="voucherType" label="Type" :error="errors?.type" /> -->
          <q-select
            v-model="voucher.type"
            error-message=""
            label="Type"
            :error="false"
            :options="['Dr', 'Cr']"
            @update:model-value="onSwitchDrCr"
          />
          <!-- <n-auto-complete v-model="voucher.account_id" :options="props.options" label="Account" :modal-component="LedgerForm" :error="errors?.account_id" /> -->
        </div>
        <div class="col-4">
          <n-auto-complete-v2
            v-model="voucher.account_id"
            label="Account"
            :endpoint="`/api/company/${$route.params.company}/journal-voucher/create-defaults/accounts/`"
            :error="
              props.errors
                ? props.errors[props.index]?.account_id
                  ? 'This field may not be null.'
                  : null
                : null
            "
            :focus-on-mount="true"
            :modal-component="checkPermissions('account.create') ? LedgerForm : null"
            :options="props.options"
            :static-option="voucher.selected_account_obj"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model.Number="voucher.dr_amount"
            class="col-6"
            label="Dr. Amount"
            min="0"
            type="number"
            :disable="voucher.type == 'Cr' || voucher.type == null"
            :error="!!props.errors?.mismatch"
            :error-message="props.errors?.mismatch"
            @focusout="focusOut"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model.Number="voucher.cr_amount"
            class="col-6"
            label="Cr. Amount"
            min="0"
            type="number"
            :disable="voucher.type == 'Dr' || voucher.type == null"
            :error="!!props.errors?.mismatch"
            :error-message="props.errors?.mismatch"
            @focusout="focusOut"
          />
        </div>
        <div class="row no-wrap items-center justify-center" style="flex-grow: 1">
          <q-btn
            flat
            class="q-pa-sm focus-highLight"
            color="transparent"
            @click.prevent="() => (openDescription = !openDescription)"
          >
            <q-icon
              class="cursor-pointer"
              color="green"
              name="mdi-arrow-expand"
              size="20px"
            >
              <q-tooltip>Expand</q-tooltip>
            </q-icon>
          </q-btn>
          <q-btn
            flat
            class="q-pa-sm focus-highLight"
            color="transparent"
            @click="deleteVoucher"
          >
            <q-icon
              class="cursor-pointer"
              color="negative"
              name="delete"
              size="20px"
            />
          </q-btn>
        </div>
      </div>
    </div>

    <div v-if="openDescription" class="row q-pb-md q-mx-xl">
      <q-input
        v-model="voucher.description"
        autogrow
        class="col-12"
        label="Description"
        type="textarea"
      />
    </div>
  </div>
</template>
