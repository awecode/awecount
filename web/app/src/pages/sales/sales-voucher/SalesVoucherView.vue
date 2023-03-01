<template>
  <q-card class="q-ma-lg">
    <q-card-section class="bg-green text-white">
      <div class="text-h6">
        <span>Sales Invoice | {{ fields.status }} | #{{ fields.voucher_no }}</span>
      </div>
    </q-card-section>
    <q-separator inset />
    <q-card class="q-mx-lg q-pt-md row">
      <div class="col-6">
        <div class="col-12 col-md-6 row">
          <div class="col-6">Party</div>
          <div class="col-6">{{ fields.party_name }}</div>
        </div>
        <div class="col-12 col-md-6 row">
          <div class="col-6">Party</div>
          <div class="col-6">{{ fields.party_name }}</div>
        </div>
        <div class="col-12 col-md-6 row">
          <div class="col-6">Party</div>
          <div class="col-6">{{ fields.party_name }}</div>
        </div>
      </div>
      <div class="col-12 col-md-6">
        2nd
      </div>
    </q-card>



    <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
      <q-btn @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="primary" label="Draft" />
      <q-btn @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green-8"
        :label="isEdit ? 'Update' : 'Issue'" />
    </div>
  </q-card>
</template>

<script>
import useApi from 'src/composables/useApi';
import { modes } from 'src/helpers/constants/invoice';
export default {
  setup() {
    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields: null,
      dialog: false,
      partyObj: null,
      modes: modes
    };
  },
  created() {
    const endpoint = `/v1/sales-voucher/${this.$route.params.id}/details/`
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' }).then((data) => {
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
    }).catch((error) => {
      if (error.response && error.response.status == 404) {
        this.$router.replace({ name: '404' });
      }
    })
  }
};
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
