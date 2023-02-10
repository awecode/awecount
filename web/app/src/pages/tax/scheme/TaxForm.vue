<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!fields.id">New Tax Scheme</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-12 col-md-6"
              :error-message="errors.name"
              :error="!!errors.name"
            />
            <q-input
              v-model="fields.short_name"
              label="Short Name"
              class="col-12 col-md-6"
              :error-message="errors.short_name"
              :error="!!errors.short_name"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.rate"
              label="Rate *"
              class="col-12 col-md-6"
              type="number"
              :error-message="errors.rate"
              :error="!!errors.rate"
            />
          </div>
          <div>
            <q-input
              v-model="fields.description"
              label="Description"
              class="col-6"
              :error-message="errors.description"
              :error="!!errors.description"
              type="textarea"
            />
          </div>
          <q-checkbox
            class="col-4"
            v-model="fields.recoverable"
            label="Is Recoverable?"
            :error-message="errors.recoverable"
            :error="!!errors.recoverable"
          />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto q-px-lg"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm';
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/tax_scheme/';
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/brand/',
      }),
    };
  },
};
</script>
