<template>
  <q-card class="q-ma-lg">
    <q-card-section class="bg-green text-white">
      <div class="text-h6">
        <span
          >Sales Invoice | {{ fields?.status }} | #{{
            fields?.voucher_no
          }}</span
        >
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
  <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
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
  </div>
</template>

<script>
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import ViewerHeader from 'src/components/viewer/ViewerHeader.vue'
import ViewerTable from 'src/components/viewer/ViewerTable.vue'
export default {
  setup() {
    const fields = ref(null)
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
