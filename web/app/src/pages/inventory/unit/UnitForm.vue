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
            <q-input v-model="fields.name" label="Name *" class="col-12" :error-message="errors.name"
              :error="!!errors.name" />
          </div>
          <div>
            <q-input v-model="fields.short_name" label="Short Name" class="col-12" :error-message="errors.short_name"
              :error="!!errors.short_name" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn type="submit" v-if="checkPermissions('UnitModify') && isEdit" :loading="loading" @click.prevent="submitForm" color="green" label="Update"
            class="q-ml-auto" />
          <q-btn type="submit" v-if="checkPermissions('UnitCreate') && !isEdit" :loading="loading" @click.prevent="submitForm" color="green" label="Create"
            class="q-ml-auto" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
const route = useRoute()
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = `/v1/${route.params.company}/units/`
    const metaData = {
      title: 'Units | Awecount',
    }
    useMeta(metaData)
    return {
      ...useForm(endpoint, {
        getDefaults: false,
        successRoute: '/units/list/',
      }), checkPermissions
    }
  },
}
</script>
