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
      successRoute: `/${route.params.company}/settings/dashboard-widgets`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Dashboard Widgets Update' : 'Dashboard Widgets Add'} | Awecount`,
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
        useApi(`/api/company/${route.params.company}/widgets/${formData.fields.value.id}/delete/`, { method: 'DELETE' })
          .then(() => {
            $q.notify({
              color: 'green-6',
              message: 'The widget has been deleted.',
              icon: 'check_circle',
            })
            router.replace(`/${route.params.company}/settings/dashboard-widgets`)
          })
          .catch((err) => {
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
  <q-form autofocus class="q-pa-lg">
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
              emit-value
              map-options
              class="col-12 col-md-6"
              label="Widget Type *"
              option-label="text"
              option-value="value"
              :error="!!errors.widget"
              :error-message="errors.widget"
              :options="formDefaults.options?.widgets"
            />
          </div>
          <div class="row">
            <q-select
              v-model="fields.display_type"
              emit-value
              map-options
              class="col-12 col-md-6"
              label="Chart Type *"
              option-label="text"
              option-value="value"
              :error="!!errors.display_type"
              :error-message="errors.display_type"
              :options="formDefaults.options?.display_types"
            />
          </div>
          <div class="row q-gutter-x-md items-center">
            <span class="q-py-sm">Show data for last</span>
            <q-input
              v-model.number="fields.count"
              label=""
              type="number"
              :error="!!errors.count"
            />
            <q-select
              v-model="fields.group_by"
              emit-value
              map-options
              label=""
              option-label="text"
              option-value="value"
              :error="!!errors.group_by"
              :error-message="errors.group_by"
              :options="formDefaults.options?.groups"
            />
          </div>
          <q-checkbox v-model="fields.is_active" label="Enabled ?" />
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg q-gutter-md justify-end">
        <q-btn
          v-if="checkPermissions('widget.create') && !isEdit"
          color="green-8"
          label="Create"
          type="submit"
          @click.prevent="submitForm"
        />
        <q-btn
          v-if="isEdit && checkPermissions('taxpayment.cancel')"
          color="red-6"
          icon="cancel"
          label="Delete"
          @click.prevent="onCancelClick"
        />
        <q-btn
          v-if="checkPermissions('widget.update') && isEdit"
          color="green-8"
          label="Update"
          type="submit"
          @click.prevent="submitForm"
        />
      </div>
    </q-card>
  </q-form>
</template>
