<template>
  <q-form class="q-pa-lg">
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
            <!-- <q-input
              v-model="fields.name"
              label="Name *"
              class="col-6"
              :error-message="errors.name"
              :error="!!errors.name"
            /> -->
            <div class="col-6">
              <n-auto-complete
                v-model="fields.item_id"
                :options="formDefaults.collections?.items"
                label="Item *"
                :error="errors?.item_id"
                :modalComponent="ItemAdd"
              />
            </div>
            <q-input
              v-model="fields.opening_balance"
              label="Opening Balance *"
              class="col-6"
              :error-message="errors.opening_balance"
              :error="!!errors.opening_balance"
              type="number"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="green"
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
import ItemAdd from '../ItemAdd.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/item-opening-balance/'
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    useMeta(metaData)
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/items/opening/',
      }),
      ItemAdd,
    }
  },
}
</script>
