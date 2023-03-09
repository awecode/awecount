<template>
  <div>
    <q-card class="q-ma-lg">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Credit Note | {{ fields?.status }} | #{{
            fields?.voucher_no
          }}</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <ViewerHeader :fields="fields" />
    </q-card>
    <div class="q-ma-lg text-subtitle2">
      Ref. Invoice No.: #{{ fields?.voucher_no }}
    </div>
    <q-card class="q-mx-lg">
      <q-card-section>
        <ViewerTable :fields="fields" />
      </q-card-section>
    </q-card>
    <!-- <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
    <q-btn
      @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
      color="primary"
      label="Draft"
    />
    <q-btn
      @click.prevent="() => onSubmitClick('Issued', fields, submitForm)"
      color="green-8"
      :label="isEdit ? 'Update' : 'Issue'"
    />
  </div> -->
    <div v-if="fields" class="q-px-lg q-pb-lg row justify-between q-gutter-x-md q-mt-md">
      <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-mb-md">
        <q-btn v-if="fields?.status === 'Draft'" color="orange-5" label="Edit" icon="edit" />
        <!-- <q-btn
            v-if="fields?.status === 'Issued'"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
            color="green-6"
            label="mark as paid"
            icon="mdi-check-all"
          /> -->
        <q-btn color="red-5" label="Cancel" icon="cancel" @click.prevent="() => (isDeleteOpen = true)" />
      </div>
      <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-gutter-y-md q-mb-md">
        <q-btn @click="onPrintclick" :label="`Print Copy No ${(fields?.print_count || 0) + 1}`" icon="print" />
        <q-btn color="blue-7" label="Journal Entries" icon="books"
          :to="`/journal-entries/credit-note/${this.$route.params.id}/`" />
      </div>
      <div v-else class="row q-gutter-x-md q-mb-md">
        <q-btn label="Print" @click="onPrintclick" icon="print" />
      </div>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6">
            <div class="text-h6 text-white">
              <span class="q-mx-md">Are you sure?</span>
            </div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="q-ma-md">
            <div class="text-right q-mt-lg row justify-between q-mx-lg">
              <q-btn label="Confirm" @click="() => submitChangeStatus(fields?.id, 'Cancelled')"></q-btn>
              <q-btn label="Deny" @click="() => (isDeleteOpen = false)"></q-btn>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </div>
</template>

<script>
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import ViewerHeader from 'src/components/viewer/ViewerHeader.vue'
import ViewerTable from 'src/components/viewer/ViewerTable.vue'
import useGeneratePdf from 'src/composables/pdf/useGeneratePdf'
export default {
  setup() {
    const fields = ref(null)
    const isDeleteOpen = ref(false)
    const submitChangeStatus = (id, status) => {
      let endpoint = ''
      let body = null
      if (status === 'Paid') {
        endpoint = `/v1/credit-note/${id}/mark_as_paid/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/v1/credit-note/${id}/cancel/`
        body = { method: 'POST' }
        debugger
      }
      useApi(endpoint, body)
        .then(() => {
          // if (fields.value)
          if (fields.value) {
            fields.value.status = status
          }
          if (status === 'Cancelled') {
            isDeleteOpen.value = false
          }
        })
        .catch((err) => console.log('err from the api', err))
    }
    const print = (bodyOnly) => {
      let ifram = document.createElement('iframe')
      ifram.style = 'display:none; margin: 20px'
      document.body.appendChild(ifram)
      const pri = ifram.contentWindow
      pri.document.open()
      pri.document.write(useGeneratePdf('creditNote', bodyOnly, fields.value))
      // pri.document.body.firstElementChild.prepend()
      pri.document.close()
      pri.focus()
      setTimeout(() => pri.print(), 100)
    }
    const onPrintclick = () => {
      const endpoint = `/v1/credit-note/${fields.value.voucher_no}/log-print/`
      useApi(endpoint, { method: 'POST' })
        .then(() => {
          if (fields.value) {
            print(false)
            fields.value.print_count = fields.value?.print_count + 1
          }
        })
        .catch((err) => console.log('err from the api', err))
    }
    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields,
      dialog: false,
      partyObj: null,
      modes: modes,
      ViewerHeader,
      ViewerTable,
      isDeleteOpen,
      submitChangeStatus,
      onPrintclick,
    }
  },
  created() {
    const endpoint = `/v1/credit-note/${this.$route.params.id}/details/`
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        // this.$set(this, 'fields', data);
        this.fields = data
        console.log(this.fields, 'data')
        // if (this.fields.party) {
        //   this.partyObj = {
        //     name: this.fields.party_name,
        //     address: this.fields.address,
        //     tax_registration_number: this.fields.tax_registration_number
        //   };
        // }
        // if (this.$route.query.pdf) {
        //   this.requestDownload();
        // }
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ name: '404' })
        }
      })
  },
}
// const {
//   columns,
//   rows,
//   resetFilters,
//   filters,
//   loading,
//   searchQuery,
//   pagination,
//   onRequest,
//   confirmDeletion,
//   initiallyLoaded,
// } = useList(endpoint);
</script>

<style>
.search-bar {
  display: flex;
  width: 100%;
  column-gap: 20px;
}

.search-bar-wrapper {
  width: 100%;
}

.filterbtn {
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
