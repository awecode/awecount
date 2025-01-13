<script>
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const $q = useQuasar()
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/inventory-settings/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '#',
    })
    const fields = ref(null)
    const metaData = {
      title: 'Inventory Settings | Awecount',
    }
    useMeta(metaData)
    const onUpdateClick = (fields) => {
      useApi(`${endpoint}${fields.id}/`, {
        method: 'PUT',
        body: fields,
      })
        .then((data) => {
          $q.notify({
            color: 'green',
            message: 'Saved!',
            icon: 'check',
          })
          fields = data
        })
        .catch((err) => {
          if (err.status === 400) {
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
    return {
      ...formData,
      fields,
      onUpdateClick,
    }
  },
}
</script>

<template>
  <q-form v-if="fields" class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Inventory Settings</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div>
          <div class="column q-gutter-y-sm q-mb-sm">
            <div>
              <q-checkbox v-model="fields.enable_fifo" label="Enable FIFO?" />
            </div>
            <div>
              <q-checkbox v-model="fields.enable_negative_stock_check" label="Enable Negative Stock Alert?" />
            </div>
          </div>
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg">
        <q-btn color="green" label="Update" type="submit" @click.prevent="() => onUpdateClick(fields)" />
      </div>
    </q-card>
  </q-form>
</template>
