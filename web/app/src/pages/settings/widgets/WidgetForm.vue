<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/widgets/`
    const $q = useQuasar()
    const router = useRouter()
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/dashboard/',
    })
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value
            ? 'Dashboard Widgets Update'
            : 'Dashboard Widgets Add'} | Awecount`,
      }
    })
    formData.fields.value.display_type = 'Table'
    formData.fields.value.count = 7
    formData.fields.value.group_by = 'Day'
    formData.fields.value.is_active = true
    const onCancelClick = async () => {
      $q.dialog({
        title: '<span class="text-red">Delete?</span>',
        message: 'Are you sure you want to delete?',
        cancel: true,
        html: true,
      }).onOk(() => {
        // submitWithStatus('Cancelled')
        useApi(`/api/company/${route.params.company}/widgets/${formData.fields.value.id}/delete/`, { method: 'DELETE' }).then(() => {
          $q.notify({
            color: 'green-6',
            message: 'The widget has been deleted.',
            icon: 'check_circle',
          })
          router.replace('/dashboard/')
        }).catch((err) => {
          if (err.status === 400) {
            $q.notify({
              color: 'red-6',
              message: err.data[0],
              icon: 'report_problem',
            })
          }
        })
      })
    }
    return {
      ...formData,
      checkPermissions,
      onCancelClick,
    }
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Widget</span>
          <span v-else>Update Widget: {{ fields.widget }}</span>
        </div>
      </q-card-section>

      <q-card-section>
        <div>
          <div class="row">
            <q-select
              v-model="fields.widget"
              class="col-12 col-md-6"
              label="Widget Type *"
              :options="formDefaults.options?.widgets"
              option-value="value"
              option-label="text"
              map-options
              emit-value
              :error="!!errors.widget"
              :error-message="errors.widget"
            />
          </div>
          <div class="row">
            <q-select
              v-model="fields.display_type"
              class="col-12 col-md-6"
              label="Chart Type *"
              :options="formDefaults.options?.display_types"
              option-value="value"
              option-label="text"
              map-options
              emit-value
              :error="!!errors.display_type"
              :error-message="errors.display_type"
            />
          </div>
          <div class="row q-gutter-x-md items-center">
            <span class="q-py-sm">Show data for last</span>
            <q-input v-model.number="fields.count" :error="!!errors.count" type="number" label="" />
            <q-select
              v-model="fields.group_by"
              :options="formDefaults.options?.groups"
              option-value="value"
              label=""
              option-label="text"
              map-options
              emit-value
              :error="!!errors.group_by"
              :error-message="errors.group_by"
            />
          </div>
          <q-checkbox v-model="fields.is_active" label="Enabled ?" />
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg q-gutter-md justify-end">
        <q-btn
          v-if="checkPermissions('WidgetCreate') && !isEdit"
          color="green-8"
          label="Create"
          type="submit"
          @click.prevent="submitForm"
        />
        <q-btn
          v-if="isEdit && checkPermissions('TaxPaymentCancel')"
          color="red-6"
          label="Delete"
          icon="cancel"
          @click.prevent="onCancelClick"
        />
        <q-btn
          v-if="checkPermissions('WidgetModify') && isEdit"
          color="green-8"
          label="Update"
          type="submit"
          @click.prevent="submitForm"
        />
      </div>
    </q-card>
  </q-form>
</template>
