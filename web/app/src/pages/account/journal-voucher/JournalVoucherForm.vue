<script>
import Decimal from 'decimal.js'

// Floating-point-error-safe subtraction
const subtract = (a, b) => {
  return new Decimal(a).minus(new Decimal(b)).toNumber()
}

const add = (a, b) => {
  return new Decimal(a).plus(new Decimal(b)).toNumber()
}

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/journal-voucher/`
    const updateVoucher = (e, i) => {
      formData.fields.value.rows[i] = e
    }
    const deleteVoucher = (i, errors) => {
      if (formData.isEdit.value) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(formData.fields.value.rows[i])
      }
      if (errors && Array.isArray(errors.rows)) {
        errors.rows.splice(i, 1)
      }
      formData.fields.value.rows.splice(i, 1)
    }
    const addNewVoucher = () => {
      const newRow = {
        type: 'Dr',
        account_id: null,
        dr_amount: null,
        cr_amount: null,
        description: null,
      }
      if (amountComputed.value.dr - amountComputed.value.cr > 0) {
        newRow.type = 'Cr'
        newRow.cr_amount = subtract(amountComputed.value.dr, amountComputed.value.cr)
      } else if (amountComputed.value.cr - amountComputed.value.dr > 0) {
        newRow.type = 'Dr'
        newRow.dr_amount = subtract(amountComputed.value.cr, amountComputed.value.dr)
      }
      formData.fields.value.rows.push(newRow)
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/account/journal-vouchers`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Journal Voucher' : 'Add Journal Voucher'} | Awecount`,
      }
    })
    formData.fields.value.voucher_no = formData?.formDefaults?.value.voucher_no || null

    watch(formData?.formDefaults, (a) => {
      if (!route.params.id) {
        formData.fields.value.voucher_no = a.fields.voucher_no || null
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today
    formData.fields.value.rows = formData.fields.value.rows || [
      {
        type: 'Dr',
        account_id: null,
        dr_amount: null,
        cr_amount: null,
        description: null,
      },
    ]

    formData.fields.value.voucher_no = formData.formDefaults.value?.fields?.voucher_no
    const amountComputed = computed(() => {
      const amount = { dr: 0, cr: 0 }
      formData.fields.value.rows.forEach((item) => {
        if (item.type === 'Dr') {
          amount.dr = add(amount.dr, Number(item.dr_amount))
        } else if (item.type === 'Cr') {
          amount.cr = add(amount.cr, Number(item.cr_amount))
        }
      })
      return amount
    })
    const checkAddVoucher = () => {
      if (amountComputed.value.dr !== amountComputed.value.cr) addNewVoucher()
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    return {
      ...formData,
      updateVoucher,
      deleteVoucher,
      addNewVoucher,
      amountComputed,
      checkAddVoucher,
      checkPermissions,
      onSubmitClick,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card class="q-pa-xs">
      <q-card-section>
        <q-card>
          <q-card-section class="bg-green text-white">
            <div class="text-h6">
              <span v-if="isEdit">Update Journal Voucher | {{ fields.status }}</span>
              <span v-else>New Journal Voucher</span>
            </div>
          </q-card-section>
          <q-card class="q-pt-md">
            <div class="row q-col-gutter-md q-px-md q-pb-md">
              <q-input
                v-model="fields.voucher_no"
                class="col-6"
                label="Voucher No."
                :error="!!errors?.voucher_no"
                :error-message="errors?.voucher_no"
              />
              <DatePicker
                v-model="fields.date"
                class="col-6"
                label="Date"
                :error="!!errors?.date"
                :error-message="errors?.date"
              />
            </div>
          </q-card>
        </q-card>
        <q-card class="q-mt-xs overflow-y-auto">
          <q-card-section class="q-pt-md min-w-[650px]">
            <div class="row q-col-gutter-md q-py-sm">
              <div class="text-center">
                SN
              </div>
              <div class="row q-col-gutter-md" style="flex-grow: 1">
                <div class="col-2">
                  Type
                </div>
                <div class="col-4">
                  Account
                </div>
                <div class="col-2">
                  Dr Amount
                </div>
                <div class="col-2">
                  Cr Amount
                </div>
                <div class="col-2"></div>
              </div>
            </div>
            <div v-for="(voucher, index) in fields.rows" :key="voucher.id">
              <VoucherRow
                :errors="errors?.rows ? errors.rows : null"
                :index="index"
                :options="formDefaults.collections?.accounts"
                :voucher="voucher"
                @check-add-voucher="checkAddVoucher"
                @delete-voucher="(index) => deleteVoucher(index, errors)"
              />
            </div>
            <div class="row q-col-gutter-md q-py-sm text-right text-bold">
              <div class="q-mr-md"></div>
              <div class="col-2"></div>
              <div class="col-3" style="text-align: right">
                Total
              </div>
              <div class="col-2" style="text-align: right">
                {{ amountComputed.dr }}
              </div>
              <div class="col-2" style="text-align: right">
                {{ amountComputed.cr }}
              </div>
              <div class="col-2"></div>
            </div>
            <q-btn
              outline
              class="q-mt-lg"
              label="ADD NEW ROW"
              style="color: green"
              @click.prevent="addNewVoucher"
            />
          </q-card-section>
        </q-card>
      </q-card-section>

      <div class="row">
        <q-input
          v-model="fields.narration"
          autogrow
          class="col-12 q-pa-md q-mb-md"
          label="Narration *"
          type="textarea"
          :error="!!errors?.narration"
          :error-message="errors?.narration"
        />
      </div>
      <div class="row q-ma-md justify-end">
        <q-btn
          v-if="checkPermissions('journalvoucher.create') && !isEdit"
          class="q-mr-md q-py-sm"
          color="orange-7"
          icon="fa-solid fa-pen-to-square"
          label="Draft"
          type="submit"
          @click.prevent="onSubmitClick('Unapproved')"
        />
        <q-btn
          v-if="checkPermissions('journalvoucher.modify') && isEdit && fields.status === 'Draft'"
          class="q-mr-md q-py-sm"
          color="orange-7"
          icon="fa-solid fa-pen-to-square"
          label="Save Draft"
          type="submit"
          @click.prevent="onSubmitClick('Unapproved')"
        />
        <q-btn
          v-if="checkPermissions('journalvoucher.create') && !isEdit"
          color="green-8"
          icon="fa-solid fa-floppy-disk"
          label="Save"
          @click.prevent="onSubmitClick('Approved')"
        />
        <q-btn
          v-if="checkPermissions('journalvoucher.modify') && isEdit"
          color="green-8"
          icon="fa-solid fa-floppy-disk"
          label="Update"
          type="submit"
          @click.prevent="onSubmitClick('Approved')"
        />
      </div>
    </q-card>
  </q-form>
</template>
