<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Widget</span>
          <span v-else>Update Widget: {{ fields.widget }}</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card-section>
        <div>
          <div class="row">
            <q-select
              class="col-12 col-md-6"
              label="Widget Type *"
              v-model="fields.widget"
              :options="formDefaults.options?.widgets"
              option-value="value"
              option-label="text"
              map-options
              emit-value
              :error="!!errors.widget"
              :error-message="errors.widget"
            />
          </div>
          <div class="row">
            <q-select
              class="col-12 col-md-6"
              label="Chart Type *"
              v-model="fields.display_type"
              :options="formDefaults.options?.display_types"
              option-value="value"
              option-label="text"
              map-options
              emit-value
              :error="!!errors.display_type"
              :error-message="errors.display_type"
            />
          </div>
          <div class="row q-gutter-x-md items-center">
            <span class="q-py-sm">Show data for last</span>
            <q-input
              v-model.number="fields.count"
              :error="!!errors.count"
              type="number"
            ></q-input>
            <q-select
              v-model="fields.group_by"
              :options="formDefaults.options?.groups"
              option-value="value"
              option-label="text"
              map-options
              emit-value
              :error="!!errors.group_by"
              :error-message="errors.group_by"
            />
          </div>
          <q-checkbox v-model="fields.is_active" label="Enabled ?">
          </q-checkbox>
        </div>
      </q-card-section>
      <div class="q-ma-md row q-pb-lg">
        <q-btn
          @click.prevent="submitForm"
          color="green-8"
          :label="isEdit ? 'Update' : 'Create'"
        />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
export default {
  setup() {
    const endpoint = 'v1/widgets/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/dashboard/',
    })
    formData.fields.value.display_type = 'Table'
    formData.fields.value.count = 7
    formData.fields.value.group_by = 'Day'
    formData.fields.value.is_active = true

    return {
      ...formData,
    }
  },
}
</script>
