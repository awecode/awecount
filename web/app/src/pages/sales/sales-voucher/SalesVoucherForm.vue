<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>Update Account</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <div class="col-6">
              <n-auto-complete
                v-model="fields.party"
                :options="formDefaults.collections?.parties"
                label="Party"
                :error="errors?.party"
                :modal-component="PartyForm"
              />
            </div>
            <q-input
              v-model="fields.date"
              class="col-6"
              label="Deposit Date*"
              :error-message="errors.date"
              :error="!!errors.date"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date v-model="fields.date" today-btn mask="YYYY-MM-DD">
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              v-model="fields.address"
              class="col-6"
              label="Address"
              :error-message="errors.address"
              :error="!!errors.address"
            ></q-input>
            <div>
              <q-input
                v-model="fields.date"
                class="col-6"
                label="Deposit Date*"
                :error-message="errors.date"
                :error="!!errors.date"
              ></q-input>
            </div>
          </div>
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
import PartyForm from 'src/pages/party/PartyForm.vue';
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/sales-voucher/';
    const openDatePicker = ref(false);
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/account/',
      }),
      CategoryForm,
      PartyForm,
      openDatePicker,
    };
  },
};
</script>
