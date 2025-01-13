<template>
  <q-form class="q-pa-lg" autofocus>
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
            <q-input v-model="fields.name" label="Name *" class="col-12 col-md-6" :error="!!errors.name" :error-message="errors.name"></q-input>
          </div>
          <div class="row">
            <q-input v-model.number="fields.compensation_multiplier" label="Compensation Multiplier *" type="number" class="col-12 col-md-6" :error="!!errors.compensation_multiplier" :error-message="errors.compensation_multiplier"></q-input>
          </div>
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg justify-end">
        <q-btn v-if="checkPermissions('SalesAgentCreate') && !isEdit" @click.prevent="submitForm" color="green" :loading="loading" label="Create" type="submit" />
        <q-btn v-if="checkPermissions('SalesAgentModify') && isEdit" @click.prevent="submitForm" color="green" :loading="loading" label="Update" type="submit" />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = 'v1/sales-agent/'
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/sales-agent/list/',
    })
    useMeta(() => {
      return {
        title: (formData.isEdit?.value ? 'Sales Agent Update' : 'Sales Agent Add') + ' | Awecount',
      }
    })
    return {
      ...formData,
      checkPermissions,
    }
  },
}
</script>
