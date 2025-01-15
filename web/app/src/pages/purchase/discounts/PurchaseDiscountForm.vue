<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/purchase-discount/`
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/purchase-discount/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Purchase Discount Update' : 'Purchase Discount Add'} | Awecount`,
      }
    })

    const type = [
      { value: 'Amount', id: 'Amount' },
      { value: 'Percent', id: 'Percent' },
    ]
    formData.fields.value.trade_discount = true
    return {
      CategoryForm,
      ...formData,
      type,
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
          <span v-if="isEdit">Update {{ fields.name }}</span>
          <span v-else>New Purchase Discount</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.name"
              class="col-12 col-md-6"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.type"
              emit-value
              map-options
              class="col-12 col-md-6"
              label="Type *"
              option-label="id"
              option-value="value"
              :error="!!errors.type"
              :error-message="errors.type"
              :options="type"
            >
              <template #append>
                <q-icon
                  v-if="fields.type !== null"
                  class="cursor-pointer"
                  name="clear"
                  @click.stop.prevent="fields.type = null"
                />
              </template>
            </q-select>
            <q-input
              v-model="fields.value"
              class="col-12 col-md-6"
              label="Value *"
              type="number"
              :error="!!errors.value"
              :error-message="errors.value"
            />
          </div>
          <q-checkbox
            v-model="fields.trade_discount"
            class="q-mt-sm"
            label="Is Trade Discount?"
            :error="!!errors.trade_discount"
            :error-message="errors.trade_discount"
          />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('purchasediscount.create') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('purchasediscount.create') && isEdit"
            class="q-ml-auto"
            color="green"
            label="Update"
            type="submit"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
