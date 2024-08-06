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
            :options="['Dr', 'Cr']"
            label="Type"
            :error-message="''"
            :error="false"
            @update:model-value="onSwitchDrCr"
          />
          <!-- <n-auto-complete v-model="voucher.account_id" :options="props.options" label="Account" :modal-component="LedgerForm" :error="errors?.account_id" /> -->
        </div>
        <div class="col-4">
          <n-auto-complete-v2
            v-model="voucher.account_id"
            label="Account"
            :options="props.options"
            :focusOnMount="true"
            :modal-component="checkPermissions('AccountCreate') ? LedgerForm : null"
            endpoint="v1/journal-voucher/create-defaults/accounts/"
            :error="
              props.errors
                ? props.errors[props.index]?.account_id
                  ? 'This field may not be null.'
                  : null
                : null
            "
            :static-option="voucher.selected_account_obj"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model.Number="voucher.dr_amount"
            type="number"
            min="0"
            label="Dr. Amount"
            class="col-6"
            :disable="voucher.type == 'Cr' || voucher.type == null"
            :error-message="props.errors?.mismatch"
            :error="!!props.errors?.mismatch"
            @focusout="focusOut"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model.Number="voucher.cr_amount"
            type="number"
            min="0"
            label="Cr. Amount"
            class="col-6"
            :disable="voucher.type == 'Dr' || voucher.type == null"
            :error-message="props.errors?.mismatch"
            :error="!!props.errors?.mismatch"
            @focusout="focusOut"
          />
        </div>
        <div
          class="row no-wrap items-center justify-center"
          style="flex-grow: 1"
        >
          <q-btn
            flat
            class="q-pa-sm focus-highLight"
            color="transparent"
            @click.prevent="() => (openDescription = !openDescription)"
          >
            <q-icon
              name="mdi-arrow-expand"
              size="20px"
              color="green"
              class="cursor-pointer"
            >
            <q-tooltip>Expand</q-tooltip>
          </q-icon>
          </q-btn>
          <q-btn
            flat
            @click="deleteVoucher"
            class="q-pa-sm focus-highLight"
            color="transparent"
          >
            <q-icon
              name="delete"
              size="20px"
              color="negative"
              class="cursor-pointer"
            ></q-icon>
          </q-btn>
        </div>
      </div>
    </div>

    <div v-if="openDescription" class="row q-pb-md q-mx-xl">
      <q-input
        v-model="voucher.description"
        type="textarea"
        autogrow
        label="Description"
        class="col-12"
      />
    </div>
  </div>
</template>

<script setup>
import LedgerForm from 'src/pages/account/ledger/LedgerForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
const props = defineProps(['voucher', 'index', 'options', 'errors'])
const emit = defineEmits(['deleteVoucher', 'checkAddVoucher'])
const voucher = ref(props.voucher)
const openDescription = ref(false)
watch(
  () => props.voucher,
  (newValue) => (voucher.value = newValue)
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
  }
  else if (mode === 'Dr') {
    voucher.value.cr_amount = null
  }
}
</script>
