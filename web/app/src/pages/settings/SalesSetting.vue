<script>
import useForm from 'src/composables/useForm'
import { modes } from 'src/helpers/constants/invoice'

export default {
  setup() {
    const $q = useQuasar()
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-settings/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '#',
    })
    const metaData = {
      title: 'Sales Settings | Awecount',
    }
    useMeta(metaData)
    const fields = ref(null)
    const modeErrors = ref(null)
    const formLoading = ref(false)
    const onUpdateClick = (fields) => {
      formLoading.value = true
      useApi(`/api/company/${route.params.company}/sales-settings/${fields.id}/`, {
        method: 'PUT',
        body: fields,
      })
        .then((data) => {
          modeErrors.value = null
          formLoading.value = false
          $q.notify({
            color: 'green',
            message: 'Saved!',
            icon: 'check',
          })
          fields.value = data
        })
        .catch((err) => {
          if (err.status === 400) {
            if (err.data.mode) {
              modeErrors.value = err.data.mode[0]
              $q.notify({
                color: 'red-6',
                message: 'Please Fill the form!',
                icon: 'report_problem',
                position: 'top-right',
              })
            }
          } else {
            modeErrors.value = null
            $q.notify({
              color: 'red-6',
              message: 'Server Error Please Contact!',
              icon: 'report_problem',
              position: 'top-right',
            })
          }
          formLoading.value = false
        })
    }
    watch(formData.formDefaults, (newValue) => (fields.value = newValue.fields))
    const modeOptionsComputed = computed(() => {
      const obj = {
        results: [{ id: null, name: 'Credit' }],
        pagination: {},
      }
      if (formData?.formDefaults.value?.collections?.payment_modes?.results) {
        obj.results = obj.results.concat(formData.formDefaults.value.collections.payment_modes.results)
        Object.assign(obj.pagination, formData.formDefaults.value.collections.payment_modes.pagination)
      }
      return obj
    })
    return {
      ...formData,
      fields,
      modes,
      onUpdateClick,
      modeErrors,
      formLoading,
      modeOptionsComputed,
    }
  },
}
</script>

<template>
  <q-form v-if="fields" class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Sales Settings</span>
        </div>
      </q-card-section>

      <q-card-section>
        <div>
          <div class="column q-gutter-y-sm q-mb-sm">
            <div>
              <q-checkbox v-model="fields.show_party_by_default" label="Show party by default?" />
            </div>
            <div>
              <q-checkbox v-model="fields.show_trade_discount_in_voucher" label="Show trade discount in voucher?" />
            </div>
            <div>
              <q-checkbox v-model="fields.is_trade_discount_in_voucher" label="Is trade discount in voucher?" />
            </div>
            <div>
              <q-checkbox v-model="fields.show_trade_discount_in_row" label="Show trade discount in row?" />
            </div>
          </div>
          <!-- <div class="row q-ml-sm">
            <div class="col-12 col-sm-6">
              <n-auto-complete-v2 label="Mode" v-model.number="fields.mode" :options="modeOptionsComputed"
                :endpoint="`/api/company/${$route.params.company}/sales-settings/create-defaults/bank_accounts" :staticOption="fields.selected_mode_obj`"
                option-value="id" option-label="name" map-options emit-value :error="!!modeErrors"
                :error-message="modeErrors">
                <template v-slot:append>
                  <q-icon v-if="fields.mode" name="close" @click.stop.prevent="fields.mode = null" class="cursor-pointer" />
                </template>
              </n-auto-complete-v2>
            </div>
          </div> -->
          <div class="row q-ml-sm">
            <div class="col-12 col-sm-6">
              <n-auto-complete-v2 v-model.number="fields.payment_mode" label="Mode" :options="modeOptionsComputed" :endpoint="`/api/company/${$route.params.company}/sales-settings/create-defaults/payment_modes`" :static-option="fields.selected_mode_obj" option-value="id" option-label="name" map-options emit-value :error="!!modeErrors" :error-message="modeErrors">
                <template #append>
                  <q-icon v-if="fields.mode" name="close" class="cursor-pointer" @click.stop.prevent="fields.mode = null" />
                </template>
              </n-auto-complete-v2>
            </div>
          </div>
          <div class="column q-gutter-y-sm q-mb-sm">
            <div>
              <q-checkbox v-model="fields.enable_row_description" label="Enable Item Description in row?" />
            </div>
            <div>
              <q-checkbox v-model="fields.enable_due_date_in_voucher" label="Enable Due date in voucher?" />
            </div>
            <div>
              <q-checkbox v-model="fields.enable_import_challan" label="Enable Challans Import?" />
            </div>
            <div>
              <q-checkbox v-model="fields.enable_amount_entry" label="Enable Amount Entry in voucher row?" />
            </div>
            <div>
              <q-checkbox v-model="fields.show_rate_quantity_in_voucher" label="Show Rate and Quantity in voucher row?" />
            </div>
            <div class="row q-pl-sm">
              <q-input v-model="fields.invoice_footer_text" class="col-12 col-sm-6" type="textarea" autogrow label="Invoice footer text" />
            </div>
            <div>
              <q-checkbox v-model="fields.persist_pos_items" label="Enable Persist items in POS page?" />
            </div>
          </div>
        </div>
        <!-- {{ formDefaults.collections }} -->
      </q-card-section>
      <div class="q-ma-md row q-pb-lg">
        <q-btn color="green" label="Update" type="submit" :loading="formLoading" @click.prevent="() => onUpdateClick(fields)" />
      </div>
    </q-card>
  </q-form>
</template>
