<template>
  <q-form class="q-pa-lg" v-if="fields" autofocus>
    <div class="row q-ml-sm">
      <div class="col-12 col-sm-6">
        <q-select map-options emit-value v-model="fields.invoice_template" option-value="value" option-label="label"
          :options="templateOptions" label="Invoicing Template" />
      </div>
    </div>
    <div class="q-ma-md row q-pb-lg">
      <q-btn @click.prevent="() => onUpdateClick(fields)" color="green" label="Update" type="submit"
        :loading="formLoading" />
    </div>
  </q-form>
</template>

<script>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useLoginStore } from 'src/stores/login-info';

export default {
  setup() {
    const $q = useQuasar()
    const loginStore = useLoginStore()
    const fields = ref({
      invoice_template: loginStore.companyInfo.invoice_template,
    })
    const formLoading = ref(false)
    const templateOptions = [
      { label: 'Template 1', value: 1 },
      { label: 'Template 2', value: 2 },
      { label: 'Template 3', value: 3 },
    ]

    const onUpdateClick = async (fields) => {
      formLoading.value = true
      const endpoint = 'v1/invoice-setting-update/'
      useApi(endpoint, {
        method: 'PATCH',
        body: { invoice_template: fields.invoice_template },
      })
        .then(() => {
          $q.notify({
            color: 'green',
            message: 'Saved!',
            icon: 'check',
          })
          loginStore.companyInfo.invoice_template = fields.invoice_template
        })
        .catch(() => {
          $q.notify({
            color: 'red-6',
            message: 'Server Error Please Contact!',
            icon: 'report_problem',
            position: 'top-right',
          })
        }).finally(() => {
          formLoading.value = false
        })
    }

    return {
      fields,
      formLoading,
      templateOptions,
      onUpdateClick,
    }
  },
}
</script>
