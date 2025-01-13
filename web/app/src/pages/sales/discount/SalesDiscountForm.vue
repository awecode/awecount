<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="isEdit">Update {{ fields.name }}</span>
          <span v-else>New Sales Discount</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.name" label="Name *" class="col-12 col-md-6" :error-message="errors.name" :error="!!errors.name" />
          </div>
          <div class="row q-col-gutter-md">
            <q-select v-model="fields.type" label="Type *" class="col-12 col-md-6" :error-message="errors.type" :error="!!errors.type" :options="type" option-value="value" option-label="id" map-options emit-value>
              <template v-slot:append>
                <q-icon v-if="fields.type !== null" class="cursor-pointer" name="clear" @click.stop.prevent="fields.type = null" />
              </template>
            </q-select>
            <q-input v-model="fields.value" label="Value *" class="col-12 col-md-6" :error-message="errors.value" :error="!!errors.value" type="number" />
          </div>
          <q-checkbox class="q-mt-sm" v-model="fields.trade_discount" label="Is Trade Discount?" :error-message="errors.trade_discount" :error="!!errors.trade_discount" />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('SalesDiscountCreate') && !isEdit" :loading="loading" @click.prevent="submitForm" color="green" label="Create" class="q-ml-auto" type="submit" />
          <q-btn v-if="checkPermissions('SalesDiscountModify') && isEdit" :loading="loading" @click.prevent="submitForm" color="green" label="Update" class="q-ml-auto" type="submit" />
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
    const endpoint = '/v1/sales-discount/'
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/sales-discount/list/',
    })
    useMeta(() => {
      return {
        title: (formData.isEdit?.value ? 'Sales Discount Update' : 'Sales Discount Add') + ' | Awecount',
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
