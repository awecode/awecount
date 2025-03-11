<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'

export default {
  setup(_props, _context) {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/accounts/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/account/ledgers`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Account Update' : 'Account Add'} | Awecount`,
      }
    })
    const categoryChoices = ref(null)
    const accountChoices = ref(null)

    useApi(`/api/company/${route.params.company}/accounts/choices/`)
      .then((res) => {
        this.accountChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
    useApi(`/api/company/${route.params.company}/categories/choices/`)
      .then((res) => {
        this.categoryChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })

    return {
      ...formData,
      CategoryForm,
      categoryChoices,
      accountChoices,
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
          <span v-if="!isEdit">New Account</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
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
            <n-auto-complete-v2
              v-if="accountChoices"
              v-model="fields.parent"
              label="Parent"
              :endpoint="`/api/company/${$route.params.company}/accounts/choices`"
              :error="errors?.parent"
              :options="accountChoices"
              :static-option="fields.selected_parent_obj"
            />
            <n-auto-complete-v2
              v-if="categoryChoices"
              v-model="fields.category"
              label="Category *"
              :endpoint="`/api/company/${$route.params.company}/categories/choices`"
              :error="errors?.category"
              :modal-component="checkPermissions('category.create') ? CategoryForm : null"
              :options="categoryChoices"
              :static-option="fields.selected_category_obj"
            />
            <n-auto-complete-v2
              v-if="accountChoices"
              v-model="fields.source"
              label="Source"
              :endpoint="`/api/company/${$route.params.company}/accounts/choices`"
              :error="errors?.source"
              :options="accountChoices"
              :static-option="fields.selected_source_obj"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('account.create') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('account.update') && isEdit"
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
