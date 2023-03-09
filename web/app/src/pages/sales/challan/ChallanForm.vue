<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Challan</span>
          <span v-else>Update Challan</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input
                    v-model="fields.customer_name"
                    label="Customer Name"
                    :error-message="errors.customer_name"
                    :error="!!errors.customer_name"
                    v-if="partyMode"
                  >
                  </q-input>
                  <n-auto-complete
                    v-else
                    v-model="fields.party"
                    :options="formDefaults.collections?.parties"
                    label="Party"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="PartyForm"
                  />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" @click="() => (partyMode = !partyMode)">
                    <q-icon name="mdi-account-group"></q-icon>
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
            >
            </q-input>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error-message="errors.address"
              :error="!!errors.address"
            ></q-input>
          </div>
        </q-card-section>
      </q-card>
      <ChallanTable
        :itemOptions="
          formDefaults.collections ? formDefaults.collections.items : null
        "
        :unitOptions="
          formDefaults.collections ? formDefaults.collections.units : null
        "
        v-model="fields.rows"
        :errors="!!errors.rows ? errors.rows : null"
        @deleteRowErr="(index) => deleteRowErr(index, errors)"
        :disableExpand="true"
      ></ChallanTable>
      <div class="q-px-md">
        <q-input
          v-model="fields.remarks"
          label="Remarks"
          type="textarea"
          autogrow
          class="col-12 col-md-10"
          :error="!!errors?.remarks"
          :error-message="errors?.remarks"
        />
      </div>
      <div class="q-ma-md row q-pb-lg">
        <q-btn
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)"
          color="green-8"
          :label="isEdit ? 'Update' : 'Create'"
        />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import ChallanTable from 'src/components/challan/ChallanTable.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/challan/'
    const openDatePicker = ref(false)
    // const $q = useQuasar()

    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/challan/list/',
    })
    const partyMode = ref(false)
    const deleteRowErr = (index, errors) => {
      errors.rows.splice(index, 1)
    }
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    formData.fields.value.date = formData.today
    formData.fields.value.party = ''
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      partyMode,
      deleteRowErr,
      onSubmitClick,
      ChallanTable,
    }
  },
}
</script>
