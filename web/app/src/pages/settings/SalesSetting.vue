<script>
import useForm from 'src/composables/useForm'
import { modes } from 'src/helpers/constants/invoice'
import { uploadFiles } from 'src/utils/file-upload'
import { parseErrors } from 'src/utils/helpers'

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
    const errors = ref({})
    const formLoading = ref(false)
    const onUpdateClick = async (fields) => {
      formLoading.value = true
      fields.default_email_attachments = await uploadFiles(fields.default_email_attachments, formData.formDefaults.value?.file_upload_paths?.default_email_attachments)
      useApi(`/api/company/${route.params.company}/sales-settings/${fields.id}/`, {
        method: 'PUT',
        body: fields,
      })
        .then((data) => {
          errors.value = {}
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
            errors.value = parseErrors(err.data)
            $q.notify({
              color: 'red-6',
              message: 'Please fill out the form correctly.',
              icon: 'report_problem',
              position: 'top-right',
            })
          } else {
            errors.value = {}
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
    watch(formData.formDefaults, newValue => (fields.value = newValue.fields))
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
      errors,
      formLoading,
      modeOptionsComputed,
    }
  },
}
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
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
          <div class="row q-ml-sm">
            <div class="col-12 col-sm-6">
              <n-auto-complete-v2
                v-model.number="fields.payment_mode"
                emit-value
                map-options
                label="Mode"
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/sales-settings/create-defaults/payment_modes`"
                :error="!!modeErrors"
                :error-message="modeErrors"
                :options="modeOptionsComputed"
                :static-option="fields.selected_mode_obj"
              >
                <template #append>
                  <q-icon
                    v-if="fields.mode"
                    class="cursor-pointer"
                    name="close"
                    @click.stop.prevent="fields.mode = null"
                  />
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
            <div>
              <q-checkbox v-model="fields.require_item_code" label="Require Item Code in sales invoices?" />
            </div>
            <div>
              <q-checkbox v-model="fields.require_item_hs_code" label="Require Item HS Code in sales invoices?" />
            </div>
            <div class="row q-pl-sm">
              <div class="col-12 col-sm-6">
                <q-label class="q-mb-md">
                  Invoice Footer Text
                </q-label>
                <q-editor
                  v-model="fields.invoice_footer_text"
                  autogrow
                />
              </div>
            </div>
            <div>
              <q-checkbox v-model="fields.persist_pos_items" label="Enable Persist items in POS page?" />
            </div>
            <file-uploader
              v-model="fields.default_email_attachments"
              multiple
              label="Default Email Attachments"
              :error="errors.default_email_attachments"
            />
          </div>
        </div>
        <!-- {{ formDefaults.collections }} -->
      </q-card-section>
      <div class="q-ma-md row q-pb-lg">
        <q-btn
          color="green"
          label="Update"
          type="submit"
          :loading="formLoading"
          @click.prevent="() => onUpdateClick(fields)"
        />
      </div>
    </q-card>
  </q-form>
</template>
