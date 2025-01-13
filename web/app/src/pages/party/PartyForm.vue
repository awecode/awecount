<script>
import checkPermissions from 'src/composables/checkPermissions'
import { useRouter } from 'vue-router'
import useForm from '/src/composables/useForm'
import PartyAlias from '/src/pages/party/PartyAlias.vue'
import PartyRepresentative from '/src/pages/party/PartyRepresentative.vue'

export default {
  components: {
    PartyRepresentative,
    PartyAlias,
  },
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const $q = useQuasar()
    const endpoint = '/v1/parties/'
    const router = useRouter()
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/party/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Party Update' : 'Party Add'} | Awecount`,
      }
    })
    const addRepresentetive = (fields) => {
      fields.representative.push({})
    }

    const addAlias = (fields) => {
      fields.aliases = fields.aliases || []
      fields.aliases.push(null)
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
      addAlias,
      addRepresentetive,
      onDeletClick,
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
          <span v-if="!isEdit">Add Party</span>
          <span v-else>Update {{ fields.name }}</span>
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
            <q-input
              v-model="fields.address"
              class="col-12 col-md-6"
              label="Address"
              :error="!!errors.address"
              :error-message="errors.address"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.contact_no"
              class="col-12 col-md-6"
              label="Contact No"
              :error="!!errors.contact_no"
              :error-message="errors.contact_no"
            />
            <q-input
              v-model="fields.email"
              class="col-12 col-md-6"
              label="Email"
              type="email"
              :error="!!errors.email"
              :error-message="errors.email"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.tax_registration_number"
              class="col-12 col-md-6"
              label="Tax Registration Number"
              type="number"
              :error="!!errors.tax_registration_number"
              :error-message="errors.tax_registration_number"
            />
          </div>
          <PartyRepresentative v-model="fields.representative" index="1" :errors="errors?.representative" />
          <PartyAlias v-model="fields.aliases" index="1" :errors="errors?.aliases" />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            outline
            class="q-mb-sm"
            color="green"
            label="Add new Alias"
            :loading="loading"
            @click.prevent="addAlias(fields)"
          />
          <span v-if="isEdit" class="flex gap-4">
            <q-btn
              outline
              class="q-mb-sm"
              color="green"
              label="Add New Representative"
              :loading="loading"
              @click.prevent="addRepresentetive(fields)"
            />
            <q-btn
              v-if="checkPermissions('PartyDelete')"
              class="q-mb-sm"
              color="red-6"
              label="Delete"
              :loading="loading"
              @click.prevent="onDeletClick"
            />
            <q-btn
              v-if="checkPermissions('PartyModify')"
              class="q-mb-sm"
              color="green"
              label="Update"
              type="submit"
              :loading="loading"
              @click.prevent="submitForm"
            />
          </span>
          <q-btn
            v-else-if="checkPermissions('PartyCreate')"
            class="q-mr-sm q-mb-sm"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
