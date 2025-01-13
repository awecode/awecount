<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from '/src/composables/useForm'

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/categories/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account-category/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Account Category Update' : 'Account Category Add'} | Awecount`,
      }
    })
    // console.log()
    // if (!formData.fields.value?.id) {
    //   formData.fields.value.id = null
    // }
    // formData.fields.value.id
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
          <span v-if="!isEdit">New Category</span>
          <span v-else>Update Category</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-mb-lg">
        <q-card-section>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <q-input
              v-model="fields.name"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
            <q-input
              v-model="fields.code"
              label="Code"
              :error="!!errors.code"
              :error-message="errors.code"
            />
          </div>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <div class="lg:col-6 col-12">
              <n-auto-complete-v2
                v-model="fields.parent"
                endpoint="v1/categories/create-defaults/categories"
                label="Parent *"
                :error="errors?.parent"
                :options="formDefaults.collections?.categories"
                :static-option="fields.selected_parent_obj"
              />
            </div>
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('CategoryModify') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('CategoryModify') && isEdit"
            class="q-ml-auto"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
