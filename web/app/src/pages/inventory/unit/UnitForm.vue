<script setup>
import { useRoute } from 'vue-router'

import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/units/`
const metaData = {
  title: 'Units | Awecount',
}
useMeta(metaData)

const { fields, errors, loading, isEdit, submitForm } = useForm(endpoint, {
  getDefaults: false,
  successRoute: `/${route.params.company}/inventory/units`,
})
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="fields.id">Update {{ fields.name }}</span>
          <span v-else>New Unit</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              class="col-12"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
          </div>
          <div>
            <q-input
              v-model="fields.short_name"
              class="col-12"
              label="Short Name"
              :error="!!errors.short_name"
              :error-message="errors.short_name"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('unit.modify') && isEdit"
            class="q-ml-auto"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('unit.create') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
