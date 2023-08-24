<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Journal Voucher | #{{ fields?.voucher_no || '-' }} |
            {{ fields?.status || '-' }}
          </span>
        </div>
      </q-card-section>

      <q-card class="q-mt-none q-ml-lg q-mr-lg text-grey-8">
        <q-card-section>
          <div class="row q-col-gutter-md q-mb-sm">
            <div class="col-6 row">
              <div class="col-6">Voucher No</div>
              <div class="col-6">{{ fields?.voucher_no || '-' }}</div>
            </div>
            <div class="col-6 row">
              <div class="col-6">Date</div>
              <div class="col-6">{{ fields?.date || '-' }}</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-card>

    <q-card class="q-mt-sm">
      <q-card-section class="">
        <!-- Head -->
        <div class="row q-col-gutter-md text-grey-9">
          <div class="col-2">SN</div>
          <div class="col-2">Type</div>
          <div class="col-grow">Account</div>
          <div class="col-2">Dr Amount</div>
          <div class="col-2">Cr Amount</div>
        </div>

        <!-- Body -->
        <div v-for="(row, index) in fields?.rows" :key="row.id" class="q-my-md">
          <hr class="q-mb-md" />
          <div class="row q-col-gutter-md">
            <div class="col-2">{{ index + 1 }}</div>
            <div class="col-2">{{ row.type }}</div>
            <div class="col-grow">
              <router-link class="text-blue text-weight-medium" style="text-decoration: none"
                :to="`/account/${row.account_id}/view/`">{{ row.account_name }}</router-link>
            </div>
            <div class="col-2">{{ row.dr_amount || 0 }}</div>
            <div class="col-2">{{ row.cr_amount || 0 }}</div>
          </div>
        </div>

        <!-- Total -->
        <div class="row q-col-gutter-md text-bold q-mt-md">
          <div class="col-2"></div>
          <div class="col-2"></div>
          <div class="col-grow">Total</div>
          <div class="col-2">
            {{
              fields?.rows?.reduce(
                (accum, item) => accum + Number(item.dr_amount),
                0
              ) || 0
            }}
          </div>
          <div class="col-2">
            {{
              fields?.rows?.reduce(
                (accum, item) => accum + Number(item.cr_amount),
                0
              ) || 0
            }}
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card class="q-mt-md" v-if="fields?.narration">
      <q-card-section>
        <div class="row">
          <div class="col-9 row text-grey-8">
            <div class="col-6">Narration</div>
            <div class="col-6">{{ fields?.narration || '-' }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <div class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs">
      <div>
        <q-btn v-if="checkPermissions('JournalVoucherModify') && fields?.status !== 'Cancelled'"
          :to="`/journal-voucher/${props.id}/edit/`" color="orange" icon="edit" label="Edit" class="text-h7 q-py-sm" />
      </div>
      <div v-if="fields?.status == 'Approved' && checkPermissions('JournalVoucherCancel')">
        <q-btn @click.prevent="prompt" color="red" icon="block" label="Cancel" class="text-h7 q-py-sm" />
      </div>
    </div>
  </q-form>
</template>

<script setup>
import useApi from 'src/composables/useApi'
import checkPermissions from 'src/composables/checkPermissions'
const props = defineProps(['id'])
const fields = ref(null)
const $q = useQuasar()
const metaData = {
  title: 'Journal Voucher | Awecount',
}
useMeta(metaData)
const getData = () =>
  useApi(`/v1/journal-voucher/${props.id}/`).then((data) => {
    fields.value = data
  })
getData()

const cancel = (data) => {
  useApi(`/v1/journal-voucher/${props.id}/cancel/`, {
    method: 'POST',
    body: { message: data },
  })
    .then(() => {
      fields.value?.status ? (fields.value.status = 'Cancelled') : ''
      $q.notify({
        color: 'positive',
        message: 'Success',
        icon: 'check_circle',
      })
    })
    .catch(() => {
      $q.notify({
        color: 'negative',
        message: 'error',
        icon: 'report_problem',
      })
    })
}

function prompt() {
  $q.dialog({
    title: 'Confirm Cancelation?',
    message: 'Reason for cancelation?',
    prompt: {
      model: '',
      type: 'text', // optional
    },
    cancel: true,
    persistent: true,
  })
    .onOk((data) => {
      cancel(data)
    })
    .onCancel(() => {
      // console.log('>>>> Cancel')
    })
    .onDismiss(() => {
      // console.log('I am triggered on both OK and Cancel')
    })
}
</script>
