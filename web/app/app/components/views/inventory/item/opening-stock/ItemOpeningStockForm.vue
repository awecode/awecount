<script>
import ItemAdd from '../ItemForm.vue'

export default {
  setup() {
    const isDeleteOpen = ref(false)
    const router = useRouter()
    const route = useRoute()
    const $q = useQuasar()
    const endpoint = `/api/company/${route.params.company}/item-opening-balance/`
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    useMeta(metaData)
    const onDeleteClick = (id) => {
      useApi(`/api/company/${route.params.company}/item-opening-balance/${id}/`, { method: 'DELETE' })
        .then(() => {
          router.push(`/${route.params.company}/inventory/opening-stock`)
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
        successRoute: `/${route.params.company}/inventory/opening-stock`,
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
  <q-form autofocus class="q-pa-lg">
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
              <n-auto-complete-v2
                v-model="fields.item_id"
                label="Item *"
                :endpoint="`/api/company/${$route.params.company}/item-opening-balance/create-defaults/items`"
                :error="errors?.item_id"
                :modal-component="ItemAdd"
                :options="formDefaults.collections?.items"
              />
            </div>
            <div v-else class="col-12 col-md-6">
              <q-input v-model="fields.name" disable />
            </div>
            <q-input
              v-model="fields.opening_balance"
              class="col-12 col-md-6"
              label="Quantity *"
              type="number"
              :error="!!errors.opening_balance"
              :error-message="errors.opening_balance"
            />
            <q-input
              v-model="fields.opening_balance_rate"
              class="col-12 col-md-6"
              label="Rate *"
              type="number"
              :error="!!errors.opening_balance_rate"
              :error-message="errors.opening_balance_rate"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-right">
          <q-btn
            v-if="isEdit && checkPermissions('accountopeningbalance.delete')"
            color="red"
            icon="delete"
            label="Delete"
            type="submit"
            :loading="loading"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="!isEdit && checkPermissions('accountopeningbalance.create')"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="isEdit && checkPermissions('accountopeningbalance.update')"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 400px)">
          <q-card-section class="bg-red-6 q-py-md flex justify-between">
            <div class="text-h6 text-white">
              <span>Delete Opening Balance ?</span>
            </div>
            <q-btn
              v-close-popup
              dense
              flat
              round
              class="text-red-700 bg-slate-200 opacity-95"
              icon="close"
            />
          </q-card-section>
          <q-separator inset />
          <q-card-section>
            <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
              Are you sure?
            </div>
            <div class="text-blue">
              <div class="row justify-end">
                <q-btn
                  flat
                  class="q-mr-md text-blue-grey-9"
                  label="NO"
                  @click="() => (isDeleteOpen = false)"
                />
                <q-btn
                  flat
                  class="text-red"
                  label="Yes"
                  @click="onDeleteClick(fields.id)"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-card>
  </q-form>
</template>
