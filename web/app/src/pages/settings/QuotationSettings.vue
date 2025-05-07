<script setup>
import { useQuasar } from 'quasar'
import useForm from 'src/composables/useForm'
import { uploadFiles } from 'src/utils/file-upload'
import { parseErrors } from 'src/utils/helpers'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const $q = useQuasar()
const route = useRoute()
const endpoint = `/api/company/${route.params.company}/quotation-settings/`
const formData = useForm(endpoint, {
  getDefaults: true,
  successRoute: '#',
})
const metaData = {
  title: 'Quotation Settings | Awecount',
}
useMeta(metaData)

const fields = ref(null)
const errors = ref({})
const formLoading = ref(false)

const onUpdateClick = async (fields) => {
  formLoading.value = true
  fields.default_email_attachments = await uploadFiles(
    fields.default_email_attachments,
    formData.formDefaults.value?.file_upload_paths?.default_email_attachments,
  )
  useApi(`/api/company/${route.params.company}/quotation-settings/${fields.id}/`, {
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

watch(formData.formDefaults, (newValue) => {
  fields.value = newValue.fields
})

const modeOptionsComputed = computed(() => {
  const obj = {
    results: [{ id: null, name: 'Credit' }],
    pagination: {},
  }
  if (formData?.formDefaults.value?.collections?.payment_modes?.results) {
    obj.results = obj.results.concat(
      formData.formDefaults.value.collections.payment_modes.results,
    )
    Object.assign(
      obj.pagination,
      formData.formDefaults.value.collections.payment_modes.pagination,
    )
  }
  return obj
})
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Quotation Settings</span>
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row q-pl-sm">
          <div class="col-12 col-sm-6">
            <q-label class="q-mb-md">
              Quotation Body Text
            </q-label>
            <q-editor
              v-model="fields.body_text"
              autogrow
            />
          </div>
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row q-pl-sm">
          <div class="col-12 col-sm-6">
            <q-label class="q-mb-md">
              Quotation Footer Text
            </q-label>
            <q-editor
              v-model="fields.footer_text"
              autogrow
            />
          </div>
        </div>
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
