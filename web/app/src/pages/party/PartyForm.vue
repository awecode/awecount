<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">Add Party</span>
          <span v-else>Update {{ fields.name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.name" label="Name *" class="col-12 col-md-6" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.address" label="Address" class="col-12 col-md-6" :error-message="errors.address"
              :error="!!errors.address" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.contact_no" label="Contact No" class="col-12 col-md-6"
              :error-message="errors.contact_no" :error="!!errors.contact_no" />
            <q-input v-model="fields.email" label="Email" class="col-12 col-md-6" :error-message="errors.email"
              :error="!!errors.email" type="email" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.tax_registration_number" type="number" label="Tax Registration Number"
              class="col-12 col-md-6" :error-message="errors.tax_registration_number"
              :error="!!errors.tax_registration_number" />
          </div>
          <PartyRepresentative v-model="fields.representative" :errors="errors?.representative" index="1">
          </PartyRepresentative>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <span v-if="isEdit" class="flex gap-4">
            <q-btn @click.prevent="addRepresentetive(fields)" color="green" outline label="Add new Representative"
              :loading="loading" class="q-mb-sm" />
            <q-btn v-if="checkPermissions('PartyDelete')" @click.prevent="onDeletClick" color="red-6" label="Delete"
              :loading="loading" class="q-mb-sm" />
            <q-btn v-if="checkPermissions('PartyModify')" @click.prevent="submitForm" color="green" label="Update"
              :loading="loading" class="q-mb-sm" type="submit" />
          </span>
          <q-btn v-else-if="checkPermissions('PartyCreate')" @click.prevent="submitForm" color="green" label="Create"
            :loading="loading" class="q-mr-sm q-mb-sm" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import PartyRepresentative from '/src/pages/party/PartyRepresentative.vue'
import checkPermissions from 'src/composables/checkPermissions'
import { useRouter } from 'vue-router'
export default {
  components: {
    PartyRepresentative,
  },
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const $q = useQuasar()
    const endpoint = '/v1/parties/'
    const router = useRouter()
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/party/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Party Update' : 'Party Add') +
          ' | Awecount',
      }
    })
    const addRepresentetive = (fields) => {
      fields.representative.push({})
    }
    function onDeletClick() {
      $q.dialog({
        title: '<span class="text-red">Delete?</span>',
        message: 'Are you sure you want to delete?',
        cancel: true,
        html: true,
      }).onOk(() => {
        // submitWithStatus('Cancelled')
        useApi(`/v1/parties/${formData.fields.value.id}/`, { method: 'DELETE' })
          .then(() => {
            router.push('/party/list/')
          })
          .catch((err) => {
            if (err.status === 400) {
              $q.notify({
                color: 'red-6',
                message: err.data[0],
                icon: 'report_problem',
              })
            }
          })
      })
    }

    return {
      ...formData,
      addRepresentetive,
      onDeletClick,
      checkPermissions
    }
  },
}
</script>
