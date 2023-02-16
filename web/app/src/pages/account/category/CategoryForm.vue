<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Category</span>
          <span v-else>Update Category</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-6"
              :error-message="errors.name || errors.detail"
              :error="!!errors.name || !!errors.detail"
            />
            <q-input
              v-model="fields.code"
              label="Code"
              class="col-6"
              :error-message="errors.code"
              :error="!!errors.code"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <n-auto-complete
                v-model="fields.parent"
                :options="formDefaults.collections?.categories"
                label="Parent"
                :error="errors?.parent"
              />
            </div>
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
    const endpoint = '/v1/category/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account/category/',
    })
    // console.log()
    // if (!formData.fields.value?.id) {
    //   formData.fields.value.id = null
    // }
    // formData.fields.value.id
    return {
      ...formData,
    }
  },
}
</script>
