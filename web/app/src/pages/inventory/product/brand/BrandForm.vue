<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/brands/`
    const metaData = {
      title: 'Brands | Awecount',
    }
    useMeta(metaData)
    return {
      ...useForm(endpoint, {
        getDefaults: false,
        successRoute: '/brand/list/',
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
          <span v-if="!isEdit">Add Brand</span>
          <span v-else>Update Brand</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-12 lg:col-6"
              :error-message="errors.name"
              :error="!!errors.name"
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
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('brand.modify') && isEdit"
            :loading="loading"
            color="green"
            label="Update"
            class="q-ml-auto"
            type="submit"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('brand.create')"
            :loading="loading"
            color="green"
            label="Create"
            class="q-ml-auto"
            type="submit"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
