<script>
import checkPermissions from '@/composables/checkPermissions'
import useForm from '@/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-agent/`
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: `/${route.params.company}/sales/agents`,
    })

    useHead({
      title: () => `${formData.isEdit?.value ? 'Sales Agent Update' : 'Sales Agent Add'} | Awecount`,
    })

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
          <span v-if="!isEdit">New Sales Agent</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>

      <q-card-section>
        <div>
          <div class="row">
            <q-input
              v-model="fields.name"
              class="col-12 col-md-6"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
          </div>
          <div class="row">
            <q-input
              v-model.number="fields.compensation_multiplier"
              class="col-12 col-md-6"
              label="Compensation Multiplier *"
              type="number"
              :error="!!errors.compensation_multiplier"
              :error-message="errors.compensation_multiplier"
            />
          </div>
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg justify-end">
        <q-btn
          v-if="checkPermissions('salesagent.create') && !isEdit"
          color="green"
          label="Create"
          type="submit"
          :loading="loading"
          @click.prevent="submitForm"
        />
        <q-btn
          v-if="checkPermissions('salesagent.update') && isEdit"
          color="green"
          label="Update"
          type="submit"
          :loading="loading"
          @click.prevent="submitForm"
        />
      </div>
    </q-card>
  </q-form>
</template>
