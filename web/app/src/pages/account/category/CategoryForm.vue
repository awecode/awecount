<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import { useRoute } from 'vue-router'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/categories/`
const { fields, errors, loading, isEdit, formDefaults, submitForm } = useForm(endpoint, {
  getDefaults: true,
  successRoute: `/${route.params.company}/account/categories`,
})

useMeta(() => ({
  title: `${isEdit.value ? 'Account Category Update' : 'Account Category Add'} | Awecount`,
}))
</script>

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
            <q-input
              v-model="fields.name"
              label="Name *"
              :error-message="errors.name"
              :error="!!errors.name"
            />
            <q-input
              v-model="fields.code"
              label="Code"
              :error-message="errors.code"
              :error="!!errors.code"
            />
          </div>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <div class="lg:col-6 col-12">
              <n-auto-complete-v2
                v-model="fields.parent"
                :options="formDefaults.collections?.categories"
                label="Parent *"
                :error="errors?.parent"
                :static-option="fields.selected_parent_obj"
                endpoint="v1/categories/create-defaults/categories"
              />
            </div>
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('CategoryModify') && !isEdit"
            type="submit"
            color="green"
            :loading="loading"
            label="Create"
            class="q-ml-auto"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('CategoryModify') && isEdit"
            type="submit"
            color="green"
            :loading="loading"
            label="Update"
            class="q-ml-auto"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
