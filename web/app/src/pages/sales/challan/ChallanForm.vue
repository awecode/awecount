<script>
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'

export default {
  setup() {
    const route = useRoute()

    const endpoint = `/api/company/${route.params.company}/challan/`
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const isDeleteOpen = ref(false)
    const deleteMsg = ref('')
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/sales/challans`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Challan Update' : 'Challan Add'} | Awecount`,
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
      if (errors && Array.isArray(errors.rows)) {
        errors.rows.splice(index, 1)
      }
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      if (formData.fields.value.party) formData.fields.value.mode = 'Credit'
      else formData.fields.value.mode = 'Cash'
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
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
    const onResolvedClick = () => {
      formData.loading.value = true
      useApi(`/api/company/${route.params.company}/challan/${formData.fields.value.id}/resolve/`, {
        method: 'POST',
        body: {},
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Marked As Resolved',
            icon: 'check_circle',
          })
          formData.fields.value.status = 'Resolved'
          formData.loading.value = false
        })
        .catch(() => {
          $q.notify({
            color: 'negative',
            message: 'error',
            icon: 'report_problem',
          })
          formData.loading.value = false
        })
    }
    const onCancelClick = () => {
      const url = `/api/company/${route.params.company}/challan/${formData.fields.value.id}/cancel/`
      const body = {
        message: deleteMsg.value,
      }
      formData.loading.value = true
      useApi(url, {
        method: 'POST',
        body,
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Cancelled',
            icon: 'check_circle',
          })
          formData.fields.value.status = 'Cancelled'
          formData.fields.value.remarks = `\nReason for cancellation: ${deleteMsg.value}`
          isDeleteOpen.value = false
          formData.loading.value = false
        })
        .catch((err) => {
          if (err.status === 422) {
            useHandleCancelInconsistencyError(url, err, body, $q)
              .then(() => {
                $q.notify({
                  color: 'positive',
                  message: 'Cancelled',
                  icon: 'check_circle',
                })
                formData.fields.value.status = 'Cancelled'
                formData.fields.value.remarks = `\nReason for cancellation: ${deleteMsg.value}`
                isDeleteOpen.value = false
                formData.loading.value = false
              })
              .catch((error) => {
                if (error.status !== 'cancel') {
                  $q.notify({
                    color: 'negative',
                    message: 'Something went Wrong!',
                    icon: 'report_problem',
                  })
                }
                formData.loading.value = false
              })
          } else {
            const parsedError = useHandleFormError(err)
            formData.errors.value = parsedError.errors
            $q.notify({
              color: 'negative',
              message: parsedError.message,
              icon: 'report_problem',
            })
          }
          formData.loading.value = false
        })
    }
    watch(
      () => formData.fields.value.party,
      (newValue) => {
        if (newValue) {
          const index = formData.formDefaults.value.collections?.parties.results.findIndex(option => option.id === newValue)
          if (index > -1) {
            formData.fields.value.address = formData.formDefaults.value.collections.parties.results[index].address
          }
        }
      },
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
      switchPartyMode,
      checkPermissions,
      onResolvedClick,
      onCancelClick,
      isDeleteOpen,
      deleteMsg,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Challan</span>
          <span v-else>
            Update Challan
            <span v-if="isEdit && fields?.voucher_no">| {{ fields?.status }} | # {{ fields?.voucher_no }}</span>
          </span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input
                    v-if="!partyMode || !!fields.customer_name"
                    v-model="fields.customer_name"
                    label="Customer Name"
                    :error="!!errors.customer_name"
                    :error-message="errors.customer_name"
                  />
                  <n-auto-complete-v2
                    v-else
                    v-model="fields.party"
                    label="Party"
                    :endpoint="`/api/company/${$route.params.company}/challan/create-defaults/parties`"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="checkPermissions('party.create') ? PartyForm : null"
                    :options="formDefaults.collections?.parties"
                    :static-option="fields.selected_party_obj"
                  />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" @click="() => switchPartyMode(fields, isEdit)">
                    <q-icon name="mdi-account-group" />
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <DatePicker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Deposit Date*"
              :error="!!errors?.date"
              :error-message="errors?.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error="!!errors.address"
              :error-message="errors.address"
            />
          </div>
        </q-card-section>
      </q-card>
      <ChallanTable
        v-if="formDefaults.collections"
        v-model="fields.rows"
        :errors="!!errors.rows ? errors.rows : null"
        :is-edit="isEdit"
        :item-options="formDefaults.collections ? formDefaults.collections.items : null"
        :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
        @delete-row="(index, deleteObj) => deleteRow(index, errors, deleteObj)"
      />
      <div class="q-px-md">
        <q-input
          v-model="fields.remarks"
          autogrow
          class="col-12 col-md-10"
          label="Remarks"
          type="textarea"
          :error="!!errors?.remarks"
          :error-message="errors?.remarks"
        />
      </div>
      <div class="q-ma-md row q-pb-lg flex justify-end q-gutter-md">
        <q-btn
          v-if="checkPermissions('challan.update') && isEdit && fields.status === 'Issued'"
          color="green"
          icon="done_all"
          label="Mark As Resolved"
          :loading="loading"
          @click.prevent="onResolvedClick"
        />
        <q-btn
          v-if="checkPermissions('challan.update') && (fields.status === 'Issued' || fields.status === 'Resolved')"
          color="red"
          icon="cancel"
          label="Cancel"
          :loading="loading"
          @click.prevent="isDeleteOpen = true"
        />
        <q-btn
          v-if="checkPermissions('challan.create') && (!isEdit || fields.status === 'Draft')"
          color="orange"
          type="submit"
          :label="isEdit ? 'Update Draft' : 'Save Draft'"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <q-btn
          v-if="checkPermissions('challan.create') && !isEdit"
          color="green"
          label="Create"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Issued')"
        />
        <q-btn
          v-if="checkPermissions('challan.update') && isEdit && fields.status !== 'Cancelled'"
          color="green"
          :label="fields.status === 'Draft' ? 'Issue From Draft' : 'Update'"
          :loading="loading"
          @click.prevent="() => onSubmitClick(fields.status === 'Draft' ? 'Issued' : fields.status)"
        />
      </div>
    </q-card>
    <q-dialog v-model="isDeleteOpen" @before-hide="delete errors.message">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6 flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn
            v-close-popup
            dense
            flat
            round
            class="text-red-700 bg-slate-200 opacity-95"
            icon="close"
          />
        </q-card-section>

        <q-card-section class="q-ma-md">
          <q-input
            v-model="deleteMsg"
            autofocus
            outlined
            type="textarea"
            :error="!!errors?.message"
            :error-message="errors?.message"
          />
          <div class="text-right q-mt-lg">
            <q-btn label="Confirm" @click="onCancelClick" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
