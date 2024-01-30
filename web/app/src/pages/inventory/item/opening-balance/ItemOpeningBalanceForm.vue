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
              <n-auto-complete v-model="fields.item_id" :options="formDefaults.collections?.items" label="Item *"
                :error="errors?.item_id" :modalComponent="ItemAdd" />
            </div>
            <div v-else class="col-12 col-md-6">
              <q-input v-model="fields.name" disable></q-input>
            </div>
            <q-input v-model="fields.opening_balance" label="Quantity *" class="col-12 col-md-6"
              :error-message="errors.opening_balance" :error="!!errors.opening_balance" type="number" />
            <q-input v-model="fields.opening_balance_rate" label="Rate *" class="col-12 col-md-6"
              :error-message="errors.opening_balance_rate" :error="!!errors.opening_balance_rate" type="number" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-right">
          <q-btn v-if="isEdit && checkPermissions('AccountOpeningBalanceDelete')" :loading="loading"
            @click.prevent="isDeleteOpen = true" icon="delete" color="red" label="Delete" type="submit" />
          <q-btn v-if="!isEdit && checkPermissions('AccountOpeningBalanceCreate')" :loading="loading"
            @click.prevent="submitForm" color="green" label="Create" type="submit" />
          <q-btn v-if="isEdit && checkPermissions('AccountOpeningBalanceModify')" :loading="loading"
            @click.prevent="submitForm" color="green" label="Update" type="submit" />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 400px)">
          <q-card-section class="bg-red-6 q-py-md flex justify-between">
            <div class="text-h6 text-white">
              <span>Delete Opening Balance ?</span>
            </div>
            <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
          </q-card-section>
          <q-separator inset />
          <q-card-section>
            <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
              Are you sure?
            </div>
            <div class=" text-blue">
              <div class="row justify-end">
                <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)"></q-btn>
                <q-btn flat class="text-red" label="Yes" @click="onDeleteClick(fields.id)"></q-btn>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-card>
  </q-form>
</template>

<script>
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/item-opening-balance/'
    const isDeleteOpen = ref(false)
    const router = useRouter()
    const $q = useQuasar()
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    useMeta(metaData)
    const onDeleteClick = (id) => {
      useApi(`/v1/item-opening-balance/${id}/`, { method: 'DELETE' }).then(() => {
        router.push('/items/opening/')
      }).catch((err) => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { errors, message } = useHandleFormError(err)
        $q.notify({
          color: 'negative',
          message: message,
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
      onDeleteClick
    }
  },
}
</script>
