<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Party</span>
          <span v-else>Update Party</span>
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
              v-model="fields.address"
              label="Address *"
              class="col-12 col-md-6"
              :error-message="errors.address"
              :error="!!errors.address"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.contact_no"
              label="Contact No"
              class="col-12 col-md-6"
              :error-message="errors.contact_no"
              :error="!!errors.contact_no"
            />
            <q-input
              v-model="fields.email"
              label="Email"
              class="col-12 col-md-6"
              :error-message="errors.email"
              :error="!!errors.email"
              type="email"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.tax_registration_number"
              type="number"
              label="Tax Registration Number"
              class="col-12 col-md-6"
              :error-message="errors.tax_registration_number"
              :error="!!errors.tax_registration_number"
            />
          </div>
          <PartyRepresentative
            v-model="fields.representative"
            :errors="errors"
          ></PartyRepresentative>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm';
import CategoryForm from '/src/pages/account/category/CategoryForm.vue';
import PartyRepresentative from '/src/pages/party/PartyRepresentative.vue';
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  components: {
    PartyRepresentative,
  },
  setup(props, context) {
    const endpoint = '/v1/parties/';
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/parties/',
      }),
      CategoryForm,
    };
  },
};
</script>
