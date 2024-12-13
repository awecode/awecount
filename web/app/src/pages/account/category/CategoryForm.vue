<template>
  <q-form class="q-pa-lg" autofocus>
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
            <q-input v-model="fields.name" label="Name *" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.code" label="Code" :error-message="errors.code"
              :error="!!errors.code" />
          </div>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <div class="lg:col-6 col-12">
              <n-auto-complete-v2 v-model="fields.parent" :options="formDefaults.collections?.categories" label="Parent *"
                :error="errors?.parent" :staticOption="fields.selected_parent_obj" endpoint="v1/categories/create-defaults/categories" />
            </div>
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('CategoryModify') && !isEdit" type="submit" @click.prevent="submitForm" color="green" :loading="loading"
            label="Create" class="q-ml-auto" />
          <q-btn v-if="checkPermissions('CategoryModify') && isEdit" type="submit" @click.prevent="submitForm" color="green" :loading="loading"
            label="Update" class="q-ml-auto" />
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
    const endpoint = `/v1/${route.params.company}/categories/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account-category/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Account Category Update'
            : 'Account Category Add') + ' | Awecount',
      }
    })
    // console.log()
    // if (!formData.fields.value?.id) {
    //   formData.fields.value.id = null
    // }
    // formData.fields.value.id
    return {
      ...formData,
      checkPermissions
    }
  },
}
</script>
