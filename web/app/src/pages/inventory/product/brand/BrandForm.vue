<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Brand</span>
          <span v-else>Update Brand</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-6"
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
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/brands/'
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/brand/',
      }),
    }
  },
}
</script>
