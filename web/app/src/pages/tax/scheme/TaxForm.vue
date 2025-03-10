<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/tax_scheme/`
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/tax/schemes/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Tax Scheme' : 'Add Tax Scheme'} | Awecount`,
      }
    })
    formData.fields.value.recoverable = false
    return {
      ...formData,
      checkPermissions,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!fields.id">New Tax Scheme</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              class="col-12 col-md-6"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
            <q-input
              v-model="fields.short_name"
              class="col-12 col-md-6"
              label="Short Name"
              :error="!!errors.short_name"
              :error-message="errors.short_name"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.rate"
              class="col-12 col-md-6"
              label="Rate *"
              type="number"
              :error="!!errors.rate"
              :error-message="errors.rate"
            />
          </div>
          <div>
            <q-input
              v-model="fields.description"
              class="col-6"
              label="Description"
              type="textarea"
              :error="!!errors.description"
              :error-message="errors.description"
            />
          </div>
          <q-checkbox
            v-model="fields.recoverable"
            class="col-4"
            label="Is Recoverable?"
            :error="!!errors.recoverable"
            :error-message="errors.recoverable"
          />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('taxscheme.create') && !isEdit"
            class="q-ml-auto q-px-lg"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('taxscheme.modify') && isEdit"
            class="q-ml-auto q-px-lg"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
