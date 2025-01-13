<script>
import ItemAdd from '../ItemAdd.vue'

export default {
  setup() {
    const endpoint = '/api/company/item-opening-balance/'
    const isDeleteOpen = ref(false)
    const router = useRouter()
    const route = useRoute()
    const $q = useQuasar()
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    useMeta(metaData)
    const onDeleteClick = (id) => {
      useApi(`/api/company/${route.params.company}/item-opening-balance/${id}/`, { method: 'DELETE' })
        .then(() => {
          router.push('/items/opening/')
        })
        .catch((err) => {
          const { message } = useHandleFormError(err)
          $q.notify({
            color: 'negative',
            message,
            icon: 'report_problem',
          })
        })
    }
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/items/opening/',
      }),
      checkPermissions,
      isDeleteOpen,
      onDeleteClick,
      ItemAdd,
    }
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Stock Opening</span>
          <span v-else>Update Stock Opening</span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div v-if="!isEdit" class="col-12 col-md-6">
              <n-auto-complete-v2 v-model="fields.item_id" :options="formDefaults.collections?.items" label="Item *" :error="errors?.item_id" :modal-component="ItemAdd" endpoint="/api/company/item-opening-balance/create-defaults/items" />
            </div>
            <div v-else class="col-12 col-md-6">
              <q-input v-model="fields.name" disable />
            </div>
            <q-input v-model="fields.opening_balance" label="Quantity *" class="col-12 col-md-6" :error-message="errors.opening_balance" :error="!!errors.opening_balance" type="number" />
            <q-input v-model="fields.opening_balance_rate" label="Rate *" class="col-12 col-md-6" :error-message="errors.opening_balance_rate" :error="!!errors.opening_balance_rate" type="number" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-right">
          <q-btn v-if="isEdit && checkPermissions('accountopeningbalance.delete')" :loading="loading" icon="delete" color="red" label="Delete" type="submit" @click.prevent="isDeleteOpen = true" />
          <q-btn v-if="!isEdit && checkPermissions('accountopeningbalance.create')" :loading="loading" color="green" label="Create" type="submit" @click.prevent="submitForm" />
          <q-btn v-if="isEdit && checkPermissions('accountopeningbalance.modify')" :loading="loading" color="green" label="Update" type="submit" @click.prevent="submitForm" />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 400px)">
          <q-card-section class="bg-red-6 q-py-md flex justify-between">
            <div class="text-h6 text-white">
              <span>Delete Opening Balance ?</span>
            </div>
            <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
          </q-card-section>
          <q-separator inset />
          <q-card-section>
            <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">Are you sure?</div>
            <div class="text-blue">
              <div class="row justify-end">
                <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)" />
                <q-btn flat class="text-red" label="Yes" @click="onDeleteClick(fields.id)" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-card>
  </q-form>
</template>
