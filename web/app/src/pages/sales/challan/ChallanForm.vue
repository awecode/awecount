<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Challan</span>
          <span v-else>Update Challan <span v-if="isEdit && fields?.voucher_no">| {{ fields?.status }} | # {{fields?.voucher_no}}</span></span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input v-model="fields.customer_name" label="Customer Name" :error-message="errors.customer_name"
                    :error="!!errors.customer_name" v-if="!partyMode || !!fields.customer_name">
                  </q-input>
                  <n-auto-complete v-else v-model="fields.party" :options="formDefaults.collections?.parties"
                    label="Party" :error="errors?.party ? errors?.party : null" :modal-component="checkPermissions('PartyCreate') ? PartyForm : null" />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" @click="() => switchPartyMode(fields, isEdit)">
                    <q-icon name="mdi-account-group"></q-icon>
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <DatePicker class="col-md-6 col-12" label="Deposit Date*" v-model="fields.date" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.address" class="col-md-6 col-12" label="Address" :error-message="errors.address"
              :error="!!errors.address"></q-input>
          </div>
        </q-card-section>
      </q-card>
      <ChallanTable :itemOptions="formDefaults.collections ? formDefaults.collections.items : null
        " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
    " v-model="fields.rows" :errors="!!errors.rows ? errors.rows : null"
        @deleteRow="(index, deleteObj) => deleteRow(index, errors, deleteObj)" :isEdit="isEdit"></ChallanTable>
      <div class="q-px-md">
        <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10"
          :error="!!errors?.remarks" :error-message="errors?.remarks" />
      </div>
      <div class="q-ma-md row q-pb-lg flex justify-end q-gutter-md">
        <q-btn v-if="checkPermissions('ChallanModify') && isEdit && fields.status === 'Issued'"
          @click.prevent="onResolvedClick" color="green" icon="done_all" label="Mark As Resolved" />
        <q-btn v-if="checkPermissions('ChallanModify') && (fields.status === 'Issued' || fields.status === 'Resolved')"
          @click.prevent="isDeleteOpen = true" color="red" label="Cancel" />
        <q-btn v-if="checkPermissions('ChallanCreate') && (!isEdit || fields.status === 'Draft')"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange" label="Draft" type="submit" />
        <q-btn v-if="checkPermissions('ChallanCreate') && !isEdit"
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green" label="Create" />
        <q-btn v-if="checkPermissions('ChallanModify') && isEdit && fields.status !== 'Cancelled'"
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green" label="Update" />
      </div>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6">
          <div class="text-h6 text-white">
            <span>Confirm Cancelation?</span>
          </div>
        </q-card-section>

        <q-card-section class="q-ma-md">
          <q-input v-model="deleteMsg" type="textarea" outlined> </q-input>
          <div class="text-right q-mt-lg">
            <q-btn label="Confirm" @click="onCancelClick"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import ChallanTable from 'src/components/challan/ChallanTable.vue'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/challan/'
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref('')
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/challan/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Challan Update' : 'Challan Add') +
          ' | Awecount',
      }
    })
    const partyMode = ref(true)
    const deleteRow = (index, errors, deleteObj) => {
      if (deleteObj) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (errors.rows) {
        errors.rows.splice(index, 1)
      }
      console.log(deleteObj)
    }
    const onSubmitClick = async (status, fields, submitForm) => {
      const originalStatus = formData.fields.value.status
      fields.status = status
      if (fields.party) fields.mode = 'Credit'
      else fields.mode = 'Cash'
      try {await submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    const switchPartyMode = (fields, isEdit) => {
      if (isEdit && !!fields.customer_name) {
        fields.customer_name = null
        partyMode.value = true
      } else {
        if (partyMode.value) {
          fields.party_name = null
          fields.party = null
        } else {
          fields.customer_name = null
        }
        partyMode.value = !partyMode.value
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.party = ''
    formData.fields.value.customer_name = null
    // onMounted(() => {
    //   if (formData.isEdit.value) {
    //     console.log(formData.fields.value)
    //     setTimeout(() => {
    //       if (!!formData.fields.value.customer_name) {
    //         partyMode.value = false
    //       }
    //     }, 100)
    //   }
    // })
    const onResolvedClick = () => {
      useApi(`/v1/challan/${formData.fields.value.id}/resolve/`, {
        method: 'POST',
        body: {},
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Marked As Resloved',
            icon: 'check_circle',
          })
          fields.value.status = 'Resloved'
        })
        .catch(() => {
          $q.notify({
            color: 'negative',
            message: 'error',
            icon: 'report_problem',
          })
        })
    }
    const onCancelClick = () => {
      useApi(`/v1/challan/${formData.fields.value.id}/cancel/`, {
        method: 'POST',
        body: {
          message: deleteMsg.value
        },
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Cancelled',
            icon: 'check_circle',
          })
          formData.fields.value.status = 'Cancelled'
          isDeleteOpen.value = false
        })
        .catch((err) => {
          let message = 'error'
          if (err.data?.message) {
            message = err.data?.message
          }
          $q.notify({
            color: 'negative',
            message,
            icon: 'report_problem',
          })
        })
    }
    watch(
      () => formData.fields.value.party,
      (newValue) => {
        if (newValue) {
          const index =
            formData.formDefaults.value.collections?.parties.findIndex(
              (option) => option.id === newValue
            )
          if (index > -1) {
            formData.fields.value.address =
              formData.formDefaults.value.collections.parties[index].address
          }
          // const index = formDefaults.
        }
      }
    )
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      partyMode,
      deleteRow,
      onSubmitClick,
      ChallanTable,
      switchPartyMode,
      checkPermissions,
      onResolvedClick,
      onCancelClick,
      isDeleteOpen,
      deleteMsg
    }
  },
  // onmounted: () => console.log('mounted'),
}
</script>
