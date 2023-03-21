<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>{{ isEdit ? 'Update' : 'Add' }} Benefactor</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-6"
              :error-message="errors.name"
              :error="!!errors.name"
            />
            <q-input
              v-model="fields.code"
              label="Code *"
              class="col-6"
              :error-message="errors.code"
              :error="!!errors.code"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <div class="col-6">
              <n-auto-complete
                v-model="fields.parent"
                :options="parent"
                label="Parent"
                :error="errors?.parent"
              />
            </div>
            <div class="col-6">
              <n-auto-complete
                v-model="fields.category"
                :options="categories"
                label="Category *"
                :modal-component="CategoryForm"
                :error="errors?.category"
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
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import useApi from '/src/composables/useApi'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const parent = ref(null)
    useApi('/v1/account/choices/').then((data) => {
      parent.value = data
    })
    const categories = ref(null)
    useApi('/v1/category/choices/').then((data) => {
      categories.value = data
    })
    const endpoint = '/v1/account/'
    return {
      ...useForm(endpoint, {
        getDefaults: true,
      }),
      CategoryForm,
      parent,
      categories,
    }
  },
}
</script>
