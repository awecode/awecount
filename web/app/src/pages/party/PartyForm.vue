<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Party</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
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
          <div class="row q-col-gutter-md">
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
          <div class="row q-col-gutter-md">
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
            :errors="errors.representative"
          ></PartyRepresentative>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg row">
          <span v-if="isEdit" class="q-gutter-x-sm row">
            <q-btn
              @click.prevent="submitForm"
              color="orange-6"
              label="Update"
              class="q-mb-sm"
            />
            <q-btn
              @click.prevent="deleteModal = true"
              color="red-6"
              label="Delete"
              class="q-mb-sm"
            />
            <q-btn
              @click.prevent="addRepresentetive(fields)"
              color="green"
              outline
              label="Add new Representative"
              class="q-mb-sm"
            />
          </span>
          <q-btn
            v-else
            @click.prevent="submitForm"
            color="primary"
            label="Create"
            class="q-mr-sm q-mb-sm"
          />
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="deleteModal">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6">
          <div class="text-h6 text-white">
            <span class="q-mx-md">Are you sure?</span>
          </div>
        </q-card-section>
        <q-separator inset />
        <q-card-section class="q-ma-md">
          <div
            class="text-right text-blue-8 q-mt-lg row justify-between q-mx-lg"
          >
            <q-btn label="Yes" @click="onDeletClick(fields)"></q-btn>
            <q-btn label="No" @click="() => (deleteModal = false)"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import PartyRepresentative from '/src/pages/party/PartyRepresentative.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  components: {
    PartyRepresentative,
  },
  setup() {
    const $q = useQuasar()
    const endpoint = '/v1/parties/'
    const addRepresentetive = (fields) => {
      fields.representative.push({})
    }
    const deleteModal = ref(false)
    function onDeletClick(fields) {
      useApi(`/v1/parties/${fields.id}/`, { method: 'DELETE' })
        .then((data) => console.log(data))
        .catch((err) => {
          if (err.status === 400) {
            $q.notify({
              color: 'red-6',
              message: err.data[0],
              icon: 'report_problem',
            })
          }
        })
    }
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/party/list/',
      }),
      addRepresentetive,
      deleteModal,
      onDeletClick,
    }
  },
}
</script>
