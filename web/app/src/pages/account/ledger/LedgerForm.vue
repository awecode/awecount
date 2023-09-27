<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Account</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.name" label="Name *" class="col-6" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.code" label="Code *" class="col-6" :error-message="errors.code"
              :error="!!errors.code" />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <n-auto-complete v-model="fields.parent" :options="accountChoices" label="Parent" :error="errors?.parent" />
            </div>
            <div class="col-6">
              <n-auto-complete v-model="fields.category" :options="categoryChoices" label="Category *"
                :modal-component="checkPermissions('CategoryCreate') ? CategoryForm : null" :error="errors?.category" />
            </div>
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('AccountCreate') && !isEdit" @click.prevent="submitForm" color="green" :loading="loading"
            label="Create" class="q-ml-auto" type="submit" />
          <q-btn v-if="checkPermissions('AccountModify') && isEdit" @click.prevent="submitForm" color="green" :loading="loading"
            label="Update" class="q-ml-auto" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/accounts/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Account Update' : 'Account Add') +
          ' | Awecount',
      }
    })
    const categoryChoices = ref(null)
    const accountChoices = ref(null)

    return {
      ...formData,
      CategoryForm,
      categoryChoices,
      accountChoices,
      checkPermissions
    }
  },
  created() {
    useApi('/v1/accounts/choices/')
      .then((res) => {
        this.accountChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
    useApi('/v1/categories/choices/')
      .then((res) => {
        this.categoryChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
  },
}
</script>
