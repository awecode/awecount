<template>
  <q-form class="q-pa-lg">
    <q-card class="q-pa-xs"
      ><q-card-section>
        <q-card>
          <q-card-section class="bg-green text-white">
            <div class="text-h6">
              <span v-if="isEdit">Update Journal Voucher</span>
              <span v-else>New Journal Voucher</span>
            </div>
          </q-card-section>
          <q-card class="q-pt-md">
            <div class="row q-col-gutter-md q-px-md q-pb-md">
              <q-input
                v-model="fields.voucher_no"
                label="Voucher No."
                class="col-6"
                :error-message="errors?.voucher_no"
                :error="!!errors?.voucher_no"
              />
              <q-input
                v-model="fields.date"
                class="col-6"
                label="Date"
                :error-message="errors?.date"
                :error="!!errors?.date"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-date v-model="fields.date" today-btn mask="YYYY-MM-DD">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </q-card>
        </q-card>
        <q-card class="q-mt-xs">
          <q-card-section class="q-pt-md">
            <div class="row q-col-gutter-md q-py-sm">
              <div class="text-center">SN</div>
              <div class="row q-col-gutter-md" style="flex-grow: 1">
                <div class="col-2">Type</div>
                <div class="col-4">Account</div>
                <div class="col-2">Dr Amount</div>
                <div class="col-2">Cr Amount</div>
                <div class="col-2"></div>
              </div>
            </div>
            <div v-for="(voucher, index) in fields.rows" :key="voucher.id">
              <VoucherRow
                :voucher="voucher"
                :index="index"
                :options="formDefaults.collections?.accounts"
                :errors="errors?.rows ? errors.rows : null"
                @updateVoucher="updateVoucher"
                @deleteVoucher="(index) => deleteVoucher(index, errors)"
              />
            </div>
            <div class="row q-col-gutter-md q-py-sm text-right text-bold">
              <div class="q-mr-md"></div>
              <div class="col-2"></div>
              <div class="col-3" style="text-align: right">Total</div>
              <div class="col-2" style="text-align: right">
                {{
                  fields.rows.reduce(
                    (accum, item) => accum + Number(item.dr_amount),
                    0
                  )
                }}
              </div>
              <div class="col-2" style="text-align: right">
                {{
                  fields.rows.reduce(
                    (accum, item) => accum + Number(item.cr_amount),
                    0
                  )
                }}
              </div>
              <div class="col-2"></div>
            </div>
            <q-btn
              @click.prevent="addNewVoucher"
              outline
              style="color: green"
              label="ADD NEW ROW"
              class="q-mt-lg"
            />
          </q-card-section>
        </q-card>
      </q-card-section>

      <div class="row">
        <q-input
          v-model="fields.narration"
          type="textarea"
          autogrow
          label="Narration *"
          class="col-12 q-pa-md q-mb-md"
          :error-message="errors?.narration"
          :error="!!errors?.narration"
        />
      </div>
    </q-card>
    <div class="row q-mt-md">
      <q-btn
        v-if="fields.status != 'Approved' || !fields?.id"
        @click.prevent=";(fields.status = 'Unapproved'), submitForm()"
        color="orange-7"
        icon="fa-solid fa-pen-to-square"
        label="Save Draft"
        class="q-mr-md q-py-sm"
      />
      <q-btn
        @click.prevent=";(fields.status = 'Approved'), submitForm()"
        color="green-8"
        icon="fa-solid fa-floppy-disk"
        :label="isEdit ? 'Update' : 'Save'"
      />
    </div>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import VoucherRow from '/src/components/VoucherRow.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/journal-voucher/'
    // const rows = ref()
    const updateVoucher = (e, i) => {
      formData.fields.value.rows[i] = e
    }
    const deleteVoucher = (i, errors) => {
      if (errors.rows) {
        errors.rows.splice(i, 1)
      }
      formData.fields.value.rows.splice(i, 1)
    }
    const addNewVoucher = () => {
      formData.fields.value.rows.push({
        type: 'Dr',
        account_id: null,
        dr_amount: null,
        cr_amount: null,
        description: null,
      })
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/journal-voucher/',
    })

    formData.fields.value.voucher_no =
      formData?.formDefaults?.value.voucher_no || null

    watch(formData?.formDefaults, (a) => {
      formData.fields.value.voucher_no = a.fields.voucher_no || null
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

    formData.fields.value.voucher_no =
      formData.formDefaults.value?.fields?.voucher_no
    const amountComputed = computed(() => {
      const amount = { dr: 0, cr: 0 }
      console.log(formData.fields)
      formData.fields.value.rows.forEach((item) => {
        console.log(item)
      })
      return fields
    })
    return {
      ...formData,
      VoucherRow,
      updateVoucher,
      deleteVoucher,
      addNewVoucher,
      amountComputed,
    }
  },
}
</script>
