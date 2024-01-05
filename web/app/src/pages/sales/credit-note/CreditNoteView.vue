<template>
  <div v-if="fields">
    <q-card class="q-ma-lg">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Credit Note | {{ fields?.status }} <span v-if="fields?.voucher_no"> | #{{ fields?.voucher_no
          }}</span></span>
        </div>
      </q-card-section>
      <ViewerHeader :fields="fields" />
    </q-card>
    <div class="q-ma-lg text-subtitle2">
      Ref. Invoice No.: #{{ fields?.invoice_data[0]?.voucher_no }}
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
        <!-- {{ fields }} -->
        <q-btn v-if="checkPermissions('CreditNoteModify') && (fields.can_update_issued || fields.status === 'Draft')"
          color="orange-5" label="Edit" icon="edit" :to="`/credit-note/${fields.id}/`" />
        <q-btn v-if="fields?.status === 'Issued'" @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
          color="green-6" label="mark as resolved" icon="mdi-check-all" />
        <q-btn v-if="checkPermissions('CreditNoteCancel')" color="red-5" label="Cancel" icon="cancel"
          @click.prevent="() => (isDeleteOpen = true)" />
      </div>
      <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-gutter-y-md q-mb-md">
        <q-btn v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
          :label="`Print ${fields.print_count > 0 ? `Copy No. ${fields.print_count}` : ''}`" icon="print"
          @click="onPrintclick(false)" />
        <q-btn v-else label="Print" icon="print" @click="onPrintclick(true)" />
        <!-- <q-btn @click="onPrintclick" label="Print" icon="print" /> -->
        <q-btn color="blue-7" label="Journal Entries" icon="books"
          :to="`/journal-entries/credit-note/${this.$route.params.id}/`" />
      </div>
      <div v-else class="row q-gutter-x-md q-mb-md">
        <q-btn label="Print" @click="onPrintclick" icon="print" />
      </div>
      <q-dialog v-model="isDeleteOpen">
          <q-card style="min-width: min(40vw, 400px)">
            <q-card-section class="bg-red-6 q-py-md">
              <div class="text-h6 text-white">
                <span>Cancel Confirmation?</span>
              </div>
            </q-card-section>
            <q-separator inset />
            <q-card-section>
              <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
                Are you sure?
              </div>
              <div class=" text-blue">
                <div class="row justify-end">
                  <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)"></q-btn>
                  <q-btn flat class="text-red" label="Yes"
                    @click="() => submitChangeStatus(fields?.id, 'Cancelled')"></q-btn>
                </div>
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
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Credit Note | Awecount',
    }
    useMeta(metaData)
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
    const onPrintclick = (noApiCall = false) => {
      if (!noApiCall) {
        const endpoint = `/v1/credit-note/${fields.value.id}/log-print/`
        useApi(endpoint, { method: 'POST' })
          .then(() => {
            if (fields.value) {
              print(false)
              fields.value.print_count = fields.value?.print_count + 1
            }
          })
          .catch((err) => console.log('err from the api', err))
      } else print(false)
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
      checkPermissions
    }
  },
  created() {
    const endpoint = `/v1/credit-note/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' }, false, true)
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
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

@media print {

  /* @import url("https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap"); */
  .d-print-none {
    display: none;
    visibility: hidden;
    width: none;
  }

  .q-card {
    box-shadow: none;
    padding: 0;
  }
}
</style>
