<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/tax_scheme/`
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/taxes/list/',
    })
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value ? 'Update Tax Scheme' : 'Add Tax Scheme'
          } | Awecount`,
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
  <q-form class="q-pa-lg" autofocus>
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
              label="Name *"
              class="col-12 col-md-6"
              :error-message="errors.name"
              :error="!!errors.name"
            />
            <q-input
              v-model="fields.short_name"
              label="Short Name"
              class="col-12 col-md-6"
              :error-message="errors.short_name"
              :error="!!errors.short_name"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.rate"
              label="Rate *"
              class="col-12 col-md-6"
              type="number"
              :error-message="errors.rate"
              :error="!!errors.rate"
            />
          </div>
          <div>
            <q-input
              v-model="fields.description"
              label="Description"
              class="col-6"
              :error-message="errors.description"
              :error="!!errors.description"
              type="textarea"
            />
          </div>
          <q-checkbox
            v-model="fields.recoverable"
            class="col-4"
            label="Is Recoverable?"
            :error-message="errors.recoverable"
            :error="!!errors.recoverable"
          />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('TaxSchemeCreate') && !isEdit"
            color="green"
            :loading="loading"
            label="Create"
            class="q-ml-auto q-px-lg"
            type="submit"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('TaxSchemeModify') && isEdit"
            color="green"
            :loading="loading"
            label="Update"
            class="q-ml-auto q-px-lg"
            type="submit"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
