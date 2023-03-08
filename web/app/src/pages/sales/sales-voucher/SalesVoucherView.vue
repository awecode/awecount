<template>
  <div v-if="fields" class="sales-invoice">
    <q-card class="q-ma-lg q-mb-sm">
      <q-card-section class="bg-green text-white">
        <div class="text-h6 d-print-none">
          <span
            >Sales Invoice | {{ fields?.status }} | #{{
              fields?.voucher_no
            }}</span
          >
        </div>
      </q-card-section>
      <q-separator inset />
      <ViewerHeader
        :fields="fields"
        :changeModes="true"
        @updateMode="(newValue) => updateMode(newValue)"
        :modeOptions="modeOptions"
      />
    </q-card>
    <q-card class="q-mx-lg" id="to_print">
      <q-card-section>
        <ViewerTable :fields="fields" />
      </q-card-section>
    </q-card>
    <q-card class="q-mx-lg q-my-md" v-if="fields?.remarks">
      <q-card-section>
        <span class="text-subtitle2 text-grey-9"> Remarks: </span>
        <span class="text-grey-9">{{ fields?.remarks }}</span>
      </q-card-section>
    </q-card>
    <div
      class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none"
      v-if="fields"
    >
      <div>
        <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md">
          <q-btn
            v-if="fields?.status === 'Draft'"
            color="orange-5"
            label="Edit"
            icon="edit"
          />
          <q-btn
            v-if="fields?.status === 'Issued'"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
            color="green-6"
            label="mark as paid"
            icon="mdi-check-all"
          />
          <q-btn
            color="red-5"
            label="Cancel"
            icon="cancel"
            @click.prevent="() => (isDeleteOpen = true)"
          />
        </div>
      </div>
      <div class="row q-gutter-x-md">
        <q-btn
          @click="() => onPrintclick(false)"
          :label="`Print Copy ${
            fields?.status !== 'Cancelled'
              ? `# ${(fields?.print_count || 0) + 1}`
              : ''
          }`"
          icon="print"
        />
        <q-btn
          @click="() => onPrintclick(true)"
          :label="`Print Body ${
            fields?.status !== 'Cancelled'
              ? `# ${(fields?.print_count || 0) + 1}`
              : ''
          }`"
          icon="print"
        />
        <q-btn
          color="blue-7"
          label="Materialized View"
          icon="mdi-table"
          :to="`/sales-voucher/${fields?.voucher_no}/mv`"
        />
        <q-btn
          v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
          color="blue-7"
          label="Journal Entries"
          icon="books"
          :to="`/journal-entries/sales-voucher/${this.$route.params.id}/`"
        />
      </div>
      <q-dialog v-model="isDeleteOpen">
        <q-card style="min-width: min(40vw, 500px)">
          <q-card-section class="bg-red-6">
            <div class="text-h6 text-white">
              <span>Confirm Cancelation?</span>
            </div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="q-ma-md">
            <q-input v-model="deleteMsg" type="textarea" outlined> </q-input>
            <div class="text-right q-mt-lg">
              <q-btn
                label="Confirm"
                @click="() => submitChangeStatus(fields?.id, 'Cancelled')"
              ></q-btn>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </div>
</template>

<script lang="ts">
import useGeneratePdf from 'src/composables/pdf/useGeneratePdf'
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import { Ref } from 'vue'

interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  mode: number
}
export default {
  setup() {
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const submitChangeStatus = (id: number, status: string) => {
      let endpoint = ''
      let body: null | object = null
      if (status === 'Paid') {
        endpoint = `/v1/sales-voucher/${id}/mark_as_paid/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/v1/sales-voucher/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
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
    const updateMode = (newValue: number) => {
      if (fields.value) {
        fields.value.mode = newValue
      }
    }
    const onPrintclick = (bodyOnly: boolean) => {
      const endpoint = `/v1/sales-voucher/${fields.value.voucher_no}/log-print/`
      useApi(endpoint, { method: 'POST' })
        .then((data) => {
          if (fields.value) {
            fields.value.print_count = fields.value?.print_count + 1
          }
          print(bodyOnly)
        })
        .catch((err) => console.log('err from the api', err))
    }
    // to print
    const print = (bodyOnly: boolean) => {
      let ifram = document.createElement('iframe')
      ifram.style = 'display:none; margin: 20px'
      document.body.appendChild(ifram)
      const pri: Record<string, string | object | HTMLElement> =
        ifram.contentWindow
      pri.document.open()
      pri.document.write(useGeneratePdf('salesVoucher', bodyOnly, fields))
      // pri.document.body.firstElementChild.prepend()
      pri.document.close()
      pri.focus()
      setTimeout(() => pri.print(), 100)
    }
    // to print

    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields,
      dialog: false,
      partyObj: null,
      modes: modes,
      submitChangeStatus,
      isDeleteOpen,
      deleteMsg,
      updateMode,
      modeOptions,
      onPrintclick,
    }
  },
  created() {
    const endpoint = `/v1/sales-voucher/${this.$route.params.id}/details/`
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
        this.modeOptions = data.available_bank_accounts
        console.log(this.fields, 'data')
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

<style lang="scss">
@media print {
  // @import url("https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap");
  .d-print-none {
    display: none;
    visibility: hidden;
    width: none;
  }
  // .sales-invoice {
  //   // background-image: url("http://localhost:8080/img/invoice_bg.png");
  //   height: 100%;
  //   // background-position: center;
  //   // background-repeat: no-repeat;
  //   background-size: cover;
  //   // height: 297mm;
  //   width: 210mm;
  //   padding: 0 5mm;
  //   .v-data-table,
  //   .v-card,
  //   thead,
  //   tr,
  //   th {
  //     background-color: transparent !important;
  //   }
  //   th,
  //   td {
  //     padding: 0.7em 0 !important;
  //     border-bottom: none !important;
  //   }
  //   th {
  //     padding-bottom: 1.5em !important;
  //   }
  // }
}
</style>
