<script setup>
import { useMeta, useQuasar } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useApi from 'src/composables/useApi'
import useForm from 'src/composables/useForm'
import PartyAlias from 'src/pages/party/PartyAlias.vue'
import PartyRepresentative from 'src/pages/party/PartyRepresentative.vue'
import { useRoute, useRouter } from 'vue-router'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const endpoint = `/api/company/${route.params.company}/parties/`

const { fields, errors, loading, isEdit, submitForm } = useForm(endpoint, {
  getDefaults: false,
  successRoute: `/${route.params.company}/party/list`,
})

useMeta(() => ({
  title: `${isEdit.value ? 'Party Update' : 'Party Add'} | Awecount`,
}))

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
    useApi(`/api/company/${route.params.company}/parties/${fields.value.id}/`, { method: 'DELETE' })
      .then(() => {
        router.push(`/${route.params.company}/party/list`)
      })
      .catch((error) => {
        console.error('Error deleting party:', error)
        $q.notify({
          color: 'negative',
          message: 'Error deleting party',
          icon: 'report_problem',
        })
      })
  })
}
</script>

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
            <q-input
              v-model="fields.name"
              label="Name *"
              class="col-12 col-md-6"
              :error-message="errors.name"
              :error="!!errors.name"
            />
            <q-input
              v-model="fields.address"
              label="Address"
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
          <PartyRepresentative v-model="fields.representative" :errors="errors?.representative" index="1" />
          <PartyAlias v-model="fields.aliases" :errors="errors?.aliases" index="1" />
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            color="green"
            outline
            label="Add new Alias"
            :loading="loading"
            class="q-mb-sm"
            @click.prevent="addAlias(fields)"
          />
          <span v-if="isEdit" class="flex gap-4">
            <q-btn
              color="green"
              outline
              label="Add New Representative"
              :loading="loading"
              class="q-mb-sm"
              @click.prevent="addRepresentetive(fields)"
            />
            <q-btn
              v-if="checkPermissions('party.delete')"
              color="red-6"
              label="Delete"
              :loading="loading"
              class="q-mb-sm"
              @click.prevent="onDeletClick"
            />
            <q-btn
              v-if="checkPermissions('party.modify')"
              color="green"
              label="Update"
              :loading="loading"
              class="q-mb-sm"
              type="submit"
              @click.prevent="submitForm"
            />
          </span>
          <q-btn
            v-else-if="checkPermissions('party.create')"
            color="green"
            label="Create"
            :loading="loading"
            class="q-mr-sm q-mb-sm"
            type="submit"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
