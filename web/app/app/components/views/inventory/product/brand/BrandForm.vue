<script>
import checkPermissions from '@/composables/checkPermissions'
import useForm from '@/composables/useForm'

export default defineNuxtComponent({
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/brands/`
    const metaData = {
      title: 'Brands | Awecount',
    }
    useHead(metaData)
    return {
      ...useForm(endpoint, {
        getDefaults: false,
        successRoute: `/${route.params.company}/inventory/brands`,
      }),
      checkPermissions,
    }
  },
})
</script>

<template>
  <q-form autofocus class="q-pa-lg">
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
              class="col-12 lg:col-6"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
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
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('brand.update') && isEdit"
            class="q-ml-auto"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('brand.create')"
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
