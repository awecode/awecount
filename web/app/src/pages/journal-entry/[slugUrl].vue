<script lang="ts">
import type { Ref } from 'vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'
// const getData = () =>
//   useApi(`/api/company/journal-voucher/${$this.route.params.id}/`).then((data) => {
//     fields.value = data
//   })
// getData()

export default {
  setup() {
    const metaData = {
      title: 'Journal Entries | Awecount',
    }
    useMeta(metaData)
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
    const seprateTransactions = ref(false)
    const store = useLoginStore()
    const getDate = computed(() => {
      if (Array.isArray(fields.value) && fields.value.length > 0) {
        const dateArray = fields?.value.map((element) => {
          return DateConverter.getRepresentation(
            element.date,
            store.isCalendarInAD ? 'ad' : 'bs',
          )
        })
        return dateArray
      } else {
        return null
      }
    })
    const getAmount = computed(() => {
      if (Array.isArray(fields.value) && fields.value.length > 0) {
        const data = fields?.value.map((element) => {
          const dr
            = element.transactions?.reduce(
              (accum: number, item: Record<string, any>) =>
                accum + Number(item.dr_amount),
              0,
            ) || 0
          const cr
            = element.transactions?.reduce(
              (accum: number, item: Record<string, any>) =>
                accum + Number(item.cr_amount),
              0,
            ) || 0
          return {
            dr_amount: dr,
            cr_amount: cr,
          }
        })
        const totalData = {
          voucherTally: data,
          totalAmount: {
            total_dr:
              data?.reduce(
                (accum: number, item: Record<string, any>) =>
                  accum + Number(item.dr_amount),
                0,
              ) || 0,
            total_cr:
              data?.reduce(
                (accum: number, item: Record<string, any>) =>
                  accum + Number(item.cr_amount),
                0,
              ) || 0,
          },
        }
        return totalData
      } else {
        return null
      }
    })
    const fields: Ref<Fields | null> = ref(null)
    const sameTransactionsData = computed(() => {
      if (Array.isArray(fields.value) && fields.value.length > 0) {
        const status = fields.value.every((item) => {
          return (item.date === fields.value[0]?.date) && (item.voucher_no === fields.value[0]?.voucher_no) && (item.source_id === fields.value[0]?.source_id)
        })
        let newTransactionObj
        if (status) {
          newTransactionObj = {}
          const fieldsConst = JSON.parse(JSON.stringify(fields.value))
          fieldsConst.forEach((parent) => {
            parent.transactions.forEach((transaction) => {
              if (newTransactionObj[`${transaction.account.id}`]) {
                newTransactionObj[`${transaction.account.id}`].cr_amount += transaction.cr_amount
                newTransactionObj[`${transaction.account.id}`].dr_amount += transaction.dr_amount
                if (newTransactionObj[`${transaction.account.id}`].cr_amount && newTransactionObj[`${transaction.account.id}`].dr_amount) {
                  const netAmount = newTransactionObj[`${transaction.account.id}`].cr_amount - newTransactionObj[`${transaction.account.id}`].dr_amount
                  if (netAmount >= 0) {
                    newTransactionObj[`${transaction.account.id}`].cr_amount = netAmount
                    newTransactionObj[`${transaction.account.id}`].dr_amount = null
                  } else {
                    newTransactionObj[`${transaction.account.id}`].cr_amount = null
                    newTransactionObj[`${transaction.account.id}`].dr_amount = (netAmount * -1)
                  }
                }
              } else {
                newTransactionObj[`${transaction.account.id}`] = transaction
              }
            })
          })
          let drIndex = 1
          let crIndex = 99999999999999
          let totalDrAmount = 0
          let totalCrAmount = 0
          for (const [key, value] of Object.entries(newTransactionObj)) {
            if (!(value.dr_amount || value.cr_amount)) {
              // Remove this object from newTransactionObj
              delete newTransactionObj[key]
              continue
            }
            if (value.dr_amount) {
              const newData = newTransactionObj[key]
              delete newTransactionObj[key]
              newTransactionObj[drIndex] = newData
              drIndex++
            } else if (value.cr_amount) {
              const newData = newTransactionObj[key]
              delete newTransactionObj[key]
              newTransactionObj[crIndex] = newData
              crIndex--
            }
            totalDrAmount += value.cr_amount || 0
            totalCrAmount += value.dr_amount || 0
          }
          newTransactionObj.total_dr = totalDrAmount
          newTransactionObj.total_cr = totalCrAmount
        }
        return newTransactionObj || false
      } else {
        return false
      }
    })
    return {
      fields,
      getDate,
      getAmount,
      sameTransactionsData,
      seprateTransactions,
    }
  },
  created() {
    const $q = useQuasar()
    const route = useRoute()
    useApi(`/api/company/${route.params.company}/${route.params.slug}/${route.params.id}/journal-entries/`)
      .then((data) => {
        this.fields = data
      })
      .catch(() => {
        $q.notify({
          color: 'negative',
          message: 'Error',
          icon: 'report_problem',
        })
      })
  },
}

// TODO: add useCase for multiple journal voucher
</script>

<template>
  <template v-if="sameTransactionsData && !seprateTransactions">
    <q-form class="q-pa-lg">
      <q-card>
        <q-card-section class="bg-grey-4 text-black">
          <div class="text-h6">
            <span>Journal Entries for
              <span class="text-capitalize">{{ fields[0]?.voucher_type }}</span> #
              {{ fields[0]?.voucher_no || '-' }}
            </span>
          </div>
        </q-card-section>
      </q-card>

      <q-card class="q-mt-sm q-pa-lg">
        <div class="row justify-between q-mb-md">
          <div class="row items-center">
            <div class="text-subtitle2 text-grey-8">
              Date :&nbsp;
            </div>
            <div class="text-bold text-grey-9">
              {{ getDate[0] || '-' }}
            </div>
          </div>
          <router-link
            v-if="$route.params.slug === 'purchase-vouchers'
              || $route.params.slug === 'sales-voucher'
            "
            style="text-decoration: none"
            :to="`/${$route.params.slug === 'purchase-vouchers'
              ? 'purchase-voucher'
              : $route.params.slug
            }/${fields[0]?.source_id}/view`"
          >
            <div class="row items-center text-blue">
              Source
            </div>
          </router-link>
        </div>
        <q-card-section class="">
          <!-- Head -->
          <div class="row q-col-gutter-md text-grey-9 text-bold q-mb-lg">
            <div class="col-grow">
              Account
            </div>
            <div class="col-3">
              DR.
            </div>
            <div class="col-3">
              CR.
            </div>
          </div>
          <!-- Body -->
          <!-- {{ sameTransactionsData }} -->
          <div v-for="(row, key, index) in sameTransactionsData" :key="key" class="q-my-md">
            <template v-if="row.dr_amount || row.cr_amount">
              <hr v-if="index !== 0" class="q-mb-md bg-grey-4 no-border" style="height: 2px" />
              <div class="row q-col-gutter-md">
                <div class="col-grow">
                  <router-link
                    style="text-decoration: none"
                    class="text-blue"
                    :to="`/account/${row.account.id}/view`"
                  >
                    {{
                      row.account.name }}
                  </router-link>
                </div>
                <div class="col-3" data-testid="dr">
                  {{ $nf(row.dr_amount) || null }}
                </div>
                <div class="col-3" data-testid="cr">
                  {{ $nf(row.cr_amount) || null }}
                </div>
              </div>
            </template>
          </div>
          <div
            class="row text-bold q-mt-md bg-grey-3 q-pa-md items-center"
            style="margin-left: -20px; margin-right: -20px"
          >
            <div class="col-grow">
              Total
            </div>
            <div class="col-3">
              {{ $nf(sameTransactionsData.total_dr) }}
            </div>
            <div class="col-3">
              {{ $nf(sameTransactionsData.total_cr) }}
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-form>
  </template>
  <template v-else>
    <q-form v-for="(voucher, index) in fields" :key="voucher.id" class="q-pa-lg">
      <q-card>
        <q-card-section class="bg-grey-4 text-black">
          <div class="text-h6">
            <span>Journal Entries for
              <span class="text-capitalize">{{ voucher.voucher_type }}</span> #
              {{ voucher?.voucher_no || '-' }}
            </span>
          </div>
        </q-card-section>
      </q-card>

      <q-card class="q-mt-sm q-pa-lg">
        <div class="row justify-between q-mb-md">
          <div class="row items-center">
            <div class="text-subtitle2 text-grey-8">
              Date :&nbsp;
            </div>
            <div class="text-bold text-grey-9">
              {{ getDate[index] || '-' }}
            </div>
          </div>
          <router-link
            v-if="$route.params.slug === 'purchase-vouchers'
              || $route.params.slug === 'sales-voucher'
            "
            style="text-decoration: none"
            :to="`/${$route.params.slug === 'purchase-vouchers'
              ? 'purchase-voucher'
              : $route.params.slug
            }/${voucher?.source_id}/view`"
          >
            <div class="row items-center text-blue">
              Source
            </div>
          </router-link>
        </div>
        <q-card-section class="">
          <!-- Head -->
          <div class="row q-col-gutter-md text-grey-9 text-bold q-mb-lg">
            <div class="col-grow">
              Account
            </div>
            <div class="col-3">
              DR.
            </div>
            <div class="col-3">
              CR.
            </div>
          </div>
          <!-- Body -->
          <div v-for="(row, index) in voucher?.transactions" :key="row.id" class="q-my-md">
            <hr v-if="index !== 0" class="q-mb-md bg-grey-4 no-border" style="height: 2px" />
            <div class="row q-col-gutter-md">
              <div class="col-grow">
                <router-link style="text-decoration: none" class="text-blue" :to="`/account/${row.account.id}/view`">
                  {{
                    row.account.name }}
                </router-link>
              </div>
              <div class="col-3" data-testid="dr">
                {{ $nf(row.dr_amount) || null }}
              </div>
              <div class="col-3" data-testid="cr">
                {{ $nf(row.cr_amount) || null }}
              </div>
            </div>
          </div>
          <div
            class="row text-bold q-mt-md bg-grey-3 q-pa-md items-center"
            style="margin-left: -20px; margin-right: -20px"
          >
            <div class="col-grow">
              Sub Total
            </div>
            <div class="col-3">
              {{ $nf(getAmount?.voucherTally[index].dr_amount) }}
            </div>
            <div class="col-3">
              {{ $nf(getAmount?.voucherTally[index].cr_amount) }}
            </div>
          </div>
        </q-card-section>
      </q-card>

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
    <q-card class="q-mt-sm q-mx-lg q-mb-xl">
      <q-card-section class="bg-grey-4">
        <div class="row text-bold">
          <div class="col-grow">
            Total
          </div>
          <div class="col-3">
            {{ $nf(sameTransactionsData.total_dr) }}
          </div>
          <div class="col-3">
            {{ $nf(sameTransactionsData.total_cr) }}
          </div>
        </div>
      </q-card-section>
    </q-card>
  </template>
  <template v-if="sameTransactionsData && fields?.length > 1">
    <div class="q-ma-md flex justify-end">
      <q-btn
        :label="seprateTransactions ? 'View Merged Transactions' : 'View Sperate Transactions'"
        color="green"
        @click="seprateTransactions = !seprateTransactions"
      />
    </div>
  </template>
</template>
