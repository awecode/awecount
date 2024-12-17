<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

const route = useRoute()
export default {
  setup() {
    const endpoint = `/api/company/${route.params.company}/units/`
    const metaData = {
      title: 'Units | Awecount',
    }
    useMeta(metaData)
    return {
      ...useForm(endpoint, {
        getDefaults: false,
        successRoute: '/units/list/',
      }),
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
          <span v-if="fields.id">Update {{ fields.name }}</span>
          <span v-else>New Unit</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-12"
              :error-message="errors.name"
              :error="!!errors.name"
            />
          </div>
          <div>
            <q-input
              v-model="fields.short_name"
              label="Short Name"
              class="col-12"
              :error-message="errors.short_name"
              :error="!!errors.short_name"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('UnitModify') && isEdit"
            type="submit"
            :loading="loading"
            color="green"
            label="Update"
            class="q-ml-auto"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('UnitCreate') && !isEdit"
            type="submit"
            :loading="loading"
            color="green"
            label="Create"
            class="q-ml-auto"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
