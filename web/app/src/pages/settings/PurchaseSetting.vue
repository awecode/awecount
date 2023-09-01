<template>
  <q-form class="q-pa-lg" v-if="fields" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Purchase Settings</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div>
          <div class="column q-gutter-y-sm q-mb-sm">
            <div>
              <q-checkbox v-model="fields.show_trade_discount_in_voucher" label="Show trade discount in voucher?">
              </q-checkbox>
            </div>
            <div>
              <q-checkbox v-model="fields.is_trade_discount_in_voucher" label="Is trade discount in voucher?">
              </q-checkbox>
            </div>
            <div>
              <q-checkbox v-model="fields.show_trade_discount_in_row" label="Show trade discount in row?">
              </q-checkbox>
            </div>
          </div>
          <div class="row q-ml-sm">
            <q-select class="col-12 col-sm-6" label="Mode" v-model.number="fields.mode" :options="formDefaults.collections.bank_accounts
              ? formDefaults.collections.bank_accounts.concat(modes)
              : modes
              " option-value="id" option-label="name" map-options emit-value :error="!!modeErrors"
              :error-message="modeErrors">
              <!-- TODO: the id of modes in field comes as string must be chnaged to number -->
              <template v-slot:append>
                <q-icon v-if="fields.mode" name="close" @click.stop.prevent="fields.mode = null" class="cursor-pointer" />
              </template>
            </q-select>
          </div>
          <div class="column q-gutter-y-sm">
            <div>
              <q-checkbox v-model="fields.enable_row_description" label="Enable Item Description in row?">
              </q-checkbox>
            </div>
            <div>
              <q-checkbox v-model="fields.enable_due_date_in_voucher" label="Enable Due date in voucher?">
              </q-checkbox>
            </div>
            <div>
              <q-checkbox v-model="fields.enable_purchase_order_import" label="Enable Purchase Orders Import?">
              </q-checkbox>
            </div>
            <div>
              <q-checkbox v-model="fields.enable_item_rate_change_alert" label="Enable Item Rate Change alert?">
              </q-checkbox>
            </div>
          </div>
          <q-card class="q-mt-lg" v-if="fields.enable_item_rate_change_alert">
                <q-card-section>
                  <div class="text-grey-7 q-mb-md"><q-icon name="info" size="sm"></q-icon> List of email address that will receive alert</div>
                  <div class=" q-mb-md">
                    <email-list v-model="fields.rate_change_alert_emails" :errors="emailListErrors" @updateErrors="onupdateErrors"/>
                  </div>
                </q-card-section>
              </q-card>
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg">
        <q-btn @click.prevent="() => onUpdateClick(fields)" color="green" label="Update" type="submit" />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import { modes } from 'src/helpers/constants/invoice'
export default {
  setup() {
    const $q = useQuasar()
    const endpoint = 'v1/purchase-settings/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '#',
    })
    const metaData = {
      title: 'Purchase Settings | Awecount',
    }
    useMeta(metaData)
    const fields = ref(null)
    const modeErrors = ref(null)
    const emailListErrors = ref(null)
    const onUpdateClick = (fields) => {
      useApi(`v1/purchase-settings/${fields.id}/`, {
        method: 'PUT',
        body: fields,
      })
        .then((data) => {
          modeErrors.value = null
          emailListErrors.value = null
          $q.notify({
            color: 'green',
            message: 'Saved!',
            icon: 'check',
          })
          fields = data
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
            if (err.data.rate_change_alert_emails) {
              emailListErrors.value = err.data.rate_change_alert_emails
              $q.notify({
                color: 'red-6',
                message: 'Please Fill the email fields properly!',
                icon: 'report_problem',
                position: 'top-right',
              })
            }
          } else {
            modeErrors.value = null
            emailListErrors.value = null
            $q.notify({
              color: 'red-6',
              message: 'Server Error Please Contact!',
              icon: 'report_problem',
              position: 'top-right',
            })
          }
        })
    }
    watch(formData.formDefaults, (newValue) => (fields.value = newValue.fields))
    const onupdateErrors = () => emailListErrors.value = null
    return {
      ...formData,
      fields,
      modes,
      onUpdateClick,
      modeErrors,
      emailListErrors,
      onupdateErrors
    }
  },
}
</script>
