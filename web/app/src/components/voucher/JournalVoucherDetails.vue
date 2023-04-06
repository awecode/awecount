<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-grey-4 text-black">
        <div class="text-h6">
          <span>Journal Entries for <span class="text-capitalize">{{ this.$route.params.slug.replace('-', ' ') }}</span>  # {{ fields?.voucher_no || '-' }} </span>
        </div>
      </q-card-section>
      <q-card class="q-mt-none q-ml-lg q-mr-lg text-grey-8">
        <q-card-section>
          <div class="row q-col-gutter-md q-mb-sm items-center justify-between">
            <div class="row items-center">
              <div class="text-subtitle2">Date :&nbsp;</div>
              <div class="text-bold text-grey-9">{{ fields?.date || '-' }}</div>
            </div>
            <router-link
              class="text-decoration-none"
              :to="`/${usedIn === 'sales_voucher' ? 'sales-voucher': (usedIn === 'debit_note' ? 'debit-note' : 'credit-note')}/${fields?.source_id}/view`"
            >
              <div class="row items-center text-blue">Source</div>
            </router-link>
          </div>
        </q-card-section>
      </q-card>
    </q-card>

    <q-card class="q-mt-sm q-pa-lg">
      <q-card-section class="">
        <!-- Head -->
        <div class="row q-col-gutter-md text-grey-9 text-bold q-mb-lg">
          <div class="col-grow">Account</div>
          <div class="col-3">DR.</div>
          <div class="col-3">CR.</div>
        </div>
        <!-- Body -->
        <div
          v-for="(row, index) in fields?.transactions"
          :key="row.id"
          class="q-my-md"
        >
          <hr
            v-if="index !== 0"
            class="q-mb-md bg-grey-4 no-border"
            style="height: 2px"
          />
          <div class="row q-col-gutter-md">
            <div class="col-grow">
              <router-link
                class="text-decoration-none text-blue"
                :to="`/ledger/${row.account.id}/`"
                >{{ row.account.name }}</router-link
              >
            </div>
            <div class="col-3">{{ row.dr_amount }}</div>
            <div class="col-3">{{ row.cr_amount }}</div>
          </div>
        </div>
        <div
          class="row text-bold q-mt-md bg-grey-3 q-pa-md items-center"
          style="margin-left: -20px; margin-right: -20px"
        >
          <div class="col-grow">Sub Total</div>
          <div class="col-3">
            {{
              fields?.transactions?.reduce(
                (accum:number, item:Record<string, any>) => accum + Number(item.dr_amount),
                0
              ) || 0
            }}
          </div>
          <div class="col-3">
            {{
              fields?.transactions?.reduce(
                (accum:number, item:Record<string, any>) => accum + Number(item.cr_amount),
                0
              ) || 0
            }}
          </div>
        </div>
      </q-card-section>
    </q-card>
    <q-card class="q-mt-md">
      <q-card-section class="bg-grey-4">
        <div class="row text-bold">
          <!-- TODO: Refactor in due time for multiple jornal entries otherWise remove -->
          <div class="col-grow">Total</div>
          <div class="col-3">
            {{
              fields?.transactions?.reduce(
                (accum:number, item:Record<string, any>) => accum + Number(item.dr_amount),
                0
              ) || 0
            }}
          </div>
          <div class="col-3">
            {{
              fields?.transactions?.reduce(
                (accum:number, item:Record<string, any>) => accum + Number(item.cr_amount),
                0
              ) || 0
            }}
          </div>
        </div>
      </q-card-section></q-card
    >
    <!-- <q-card class="q-mt-md" v-if="fields?.narration">
      <q-card-section>
        <div class="row">
          <div class="col-9 row text-grey-8">
            <div class="col-6">Narration</div>
            <div class="col-6">{{ fields?.narration || '-' }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card> -->
    <!-- <div class="q-pr-md q-pb-lg row q-col-gutter-md q-mt-xs">
      <div>
        <q-btn
          :to="`/journal-voucher/${fields?.id}/edit/`"
          color="orange"
          icon="edit"
          label="Edit"
          class="text-h7 q-py-sm"
        />
      </div>
      <div v-if="fields?.status == 'Approved'">
        <q-btn
          @click.prevent="prompt"
          color="red"
          icon="block"
          label="Cancel"
          class="text-h7 q-py-sm"
        />
      </div>
    </div> -->
  </q-form>
</template>

<script lang="ts">
export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
    title: {
      type: String,
      default: () => {
        return 'Journal Entries'
      },
    },
    usedIn: {
      type: String,
      default: () => {
        return null
      },
    },
  },
  setup(props) {
    const $q = useQuasar()
    interface Fields {
      total_amount: number
      voucher_number: number
      status: string
      voucher_no: number
      date: string
      rows: Array<Record<string, number | boolean | string>>
      narration: string
      id: number
    }
    return {
      props,
    }
  },
  // created() {
  //   const endpoint = `v1/sales-voucher/${this.$route.params.id}/journal-entries/`
  //   console.log(endpoint)
  //   useApi(endpoint, { method: 'GET' })
  //     .then((data) => {
  //       this.fields = data[0]
  //       console.log('fields', this.fields)
  //     })
  //     .catch((error) => {
  //       if (error.response && error.response.status == 404) navigateTo('404')
  //     })
  // },
}

// const cancel = (data) => {
//   useApi(`/v1/journal-voucher/${props.id}/cancel/`, {
//     method: 'POST',
//     body: { message: data },
//   })
//     .then(() => {
//       fields.value?.status ? (fields.value.status = 'Cancelled') : ''
//       $q.notify({
//         color: 'positive',
//         message: 'Success',
//         icon: 'check_circle',
//       })
//     })
//     .catch(() => {
//       $q.notify({
//         color: 'negative',
//         message: 'error',
//         icon: 'report_problem',
//       })
//     })
// }

// function prompt() {
//   $q.dialog({
//     title: 'Confirm Cancelation?',
//     message: 'Reason for cancelation?',
//     prompt: {
//       model: '',
//       type: 'text', // optional
//     },
//     cancel: true,
//     persistent: true,
//   })
//     .onOk((data) => {
//       cancel(data)
//     })
//     .onCancel(() => {
//       // console.log('>>>> Cancel')
//     })
//     .onDismiss(() => {
//       // console.log('I am triggered on both OK and Cancel')
//     })
// }
</script>

<style scoped>
.text-decoration-none {
  text-decoration: none;
}
</style>
