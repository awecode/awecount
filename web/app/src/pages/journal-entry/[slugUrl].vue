<script setup lang="ts">
import Decimal from 'decimal.js'
import { useMeta, useQuasar } from 'quasar'
import DateConverter from 'src/components/date/VikramSamvat.js'
import FormattedNumber from 'src/components/FormattedNumber.vue'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

interface Transaction {
  account: {
    id: number
    name: string
  }
  dr_amount: number | null
  cr_amount: number | null
}

interface Voucher {
  total_amount: number
  voucher_number: number
  status: string
  voucher_no: number
  date: string
  voucher_type: string
  source_id?: number
  transactions: Transaction[]
  narration: string
  id: number
}

interface TransactionData {
  [key: string]: {
    account: {
      id: number
      name: string
    }
    dr_amount: number | null
    cr_amount: number | null
  } | number
  total_dr: number
  total_cr: number
}

useMeta({
  title: 'Journal Entries | Awecount',
})

const $q = useQuasar()
const route = useRoute()
const store = useLoginStore()

const fields = ref<Voucher[] | null>(null)
const separateTransactions = ref(false)

const getDate = computed(() => {
  if (Array.isArray(fields.value) && fields.value.length > 0) {
    return fields.value.map((element) => {
      return DateConverter.getRepresentation(element.date, store.isCalendarInAD ? 'ad' : 'bs')
    })
  }
  return null
})

const getAmount = computed(() => {
  if (Array.isArray(fields.value) && fields.value.length > 0) {
    const data = fields.value.map((element) => {
      const dr = element.transactions?.reduce((accum: Decimal, item: Transaction) => accum.add(new Decimal(item.dr_amount || '0')), new Decimal('0')).toNumber() || 0
      const cr = element.transactions?.reduce((accum: Decimal, item: Transaction) => accum.add(new Decimal(item.cr_amount || '0')), new Decimal('0')).toNumber() || 0
      return {
        dr_amount: dr,
        cr_amount: cr,
      }
    })
    return {
      voucherTally: data,
      totalAmount: {
        total_dr: data?.reduce((accum: Decimal, item) => accum.add(new Decimal(item.dr_amount || '0')), new Decimal('0')).toNumber() || 0,
        total_cr: data?.reduce((accum: Decimal, item) => accum.add(new Decimal(item.cr_amount || '0')), new Decimal('0')).toNumber() || 0,
      },
    }
  }
  return null
})

const sameTransactionsData = computed<TransactionData | false>(() => {
  if (Array.isArray(fields.value) && fields.value.length > 0) {
    const status = fields.value.every((item) => {
      return item.date === fields.value[0]?.date
        && item.voucher_no === fields.value[0]?.voucher_no
        && item.source_id === fields.value[0]?.source_id
    })

    if (status) {
      const newTransactionObj: TransactionData = {
        total_dr: 0,
        total_cr: 0,
      }
      const fieldsConst = JSON.parse(JSON.stringify(fields.value))

      fieldsConst.forEach((parent) => {
        parent.transactions.forEach((transaction) => {
          const accountId = transaction.account.id.toString()
          if (newTransactionObj[accountId]) {
            const existing = newTransactionObj[accountId] as Transaction
            existing.cr_amount = new Decimal(existing.cr_amount || '0')
              .add(new Decimal(transaction.cr_amount || '0'))
              .toNumber()
            existing.dr_amount = new Decimal(existing.dr_amount || '0')
              .add(new Decimal(transaction.dr_amount || '0'))
              .toNumber()

            if (existing.cr_amount && existing.dr_amount) {
              const netAmount = new Decimal(existing.cr_amount || '0')
                .sub(new Decimal(existing.dr_amount || '0'))
                .toNumber()
              if (netAmount >= 0) {
                existing.cr_amount = netAmount
                existing.dr_amount = null
              } else {
                existing.cr_amount = null
                existing.dr_amount = new Decimal(netAmount).abs().toNumber()
              }
            }
          } else {
            newTransactionObj[accountId] = { ...transaction }
          }
        })
      })

      let drIndex = 1
      let crIndex = 99999999999999
      let totalDrAmount = new Decimal('0')
      let totalCrAmount = new Decimal('0')

      for (const [key, value] of Object.entries(newTransactionObj)) {
        if (key === 'total_dr' || key === 'total_cr') continue

        if (typeof value === 'number') continue

        if (!(value.dr_amount || value.cr_amount)) {
          delete newTransactionObj[key]
          continue
        }

        if (value.dr_amount) {
          const newData = newTransactionObj[key] as Transaction
          delete newTransactionObj[key]
          newTransactionObj[drIndex] = newData
          drIndex++
        } else if (value.cr_amount) {
          const newData = newTransactionObj[key] as Transaction
          delete newTransactionObj[key]
          newTransactionObj[crIndex] = newData
          crIndex--
        }

        totalDrAmount = totalDrAmount.add(new Decimal(value.cr_amount || '0'))
        totalCrAmount = totalCrAmount.add(new Decimal(value.dr_amount || '0'))
      }

      newTransactionObj.total_dr = totalDrAmount.toNumber()
      newTransactionObj.total_cr = totalCrAmount.toNumber()

      return newTransactionObj
    }
  }
  return false
})

const CONTENT_TYPE_TO_SLUG = {
  'purchase-vouchers': 'purchase/vouchers',
  'sales-vouchers': 'sales/vouchers',
  'sales-voucher': 'sales/vouchers',
  'debit-notes': 'purchase/debit-notes',
  'credit-notes': 'sales/credit-notes',
  'challans': 'sales/challans',
  'payment-receipts': 'payment-receipts',
} as const

// Fetch data on component mount
useApi(`/api/company/${route.params.company}/${route.params.slug}/${route.params.id}/journal-entries/`)
  .then((data) => {
    fields.value = data
  })
  .catch(() => {
    $q.notify({
      color: 'negative',
      message: 'Error',
      icon: 'report_problem',
    })
  })
</script>

<template>
  <template v-if="sameTransactionsData && !separateTransactions">
    <q-form class="q-pa-lg">
      <q-card>
        <q-card-section class="bg-grey-4 text-black">
          <div class="text-h6">
            <span>
              Journal Entries for
              <span class="text-capitalize">{{ fields?.[0]?.voucher_type }}</span>
              #
              {{ fields?.[0]?.voucher_no || '-' }}
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
              {{ getDate?.[0] || '-' }}
            </div>
          </div>
          <router-link
            v-if="route.params.slug === 'purchase-vouchers' || route.params.slug === 'sales-voucher'"
            style="text-decoration: none"
            :to="`/${route.params.company}/${CONTENT_TYPE_TO_SLUG[route.params.slug as keyof typeof CONTENT_TYPE_TO_SLUG]}/${fields?.[0]?.source_id}`"
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
          <div v-for="(row, key) in sameTransactionsData" :key="key" class="q-my-md">
            <template v-if="key !== 'total_dr' && key !== 'total_cr' && typeof row !== 'number' && (row.dr_amount || row.cr_amount)">
              <hr v-if="key !== '1'" class="q-mb-md bg-grey-4 no-border" style="height: 2px" />
              <div class="row q-col-gutter-md">
                <div class="col-grow">
                  <router-link class="text-blue" style="text-decoration: none" :to="`/${route.params.company}/account/ledgers/${row.account.id}`">
                    {{ row.account.name }}
                  </router-link>
                </div>
                <div class="col-3" data-testid="dr">
                  <FormattedNumber
                    null-value="-"
                    type="currency"
                    zero-value="-"
                    :value="row.dr_amount"
                  />
                </div>
                <div class="col-3" data-testid="cr">
                  <FormattedNumber
                    null-value="-"
                    type="currency"
                    zero-value="-"
                    :value="row.cr_amount"
                  />
                </div>
              </div>
            </template>
          </div>
          <div class="row text-bold q-mt-md bg-grey-3 q-pa-md items-center" style="margin-left: -20px; margin-right: -20px">
            <div class="col-grow">
              Total
            </div>
            <div class="col-3" style="padding-left: 12px">
              <FormattedNumber
                v-if="sameTransactionsData"
                null-value="-"
                type="currency"
                :value="sameTransactionsData.total_dr"
              />
            </div>
            <div class="col-3" style="padding-left: 12px">
              <FormattedNumber
                v-if="sameTransactionsData"
                null-value="-"
                type="currency"
                :value="sameTransactionsData.total_cr"
              />
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
            <span>
              Journal Entries for
              <span class="text-capitalize">{{ voucher.voucher_type }}</span>
              #
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
              {{ getDate?.[index] || '-' }}
            </div>
          </div>
          <router-link
            v-if="route.params.slug === 'purchase-vouchers' || route.params.slug === 'sales-voucher'"
            style="text-decoration: none"
            :to="`/${route.params.company}/${CONTENT_TYPE_TO_SLUG[route.params.slug as keyof typeof CONTENT_TYPE_TO_SLUG]}/${voucher?.source_id}`"
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
          <div v-for="(row, idx) in voucher?.transactions" :key="idx" class="q-my-md">
            <hr v-if="idx !== 0" class="q-mb-md bg-grey-4 no-border" style="height: 2px" />
            <div class="row q-col-gutter-md">
              <div class="col-grow">
                <router-link class="text-blue" style="text-decoration: none" :to="`/${route.params.company}/account/ledgers/${row.account.id}`">
                  {{ row.account.name }}
                </router-link>
              </div>
              <div class="col-3" data-testid="dr">
                <FormattedNumber
                  null-value="-"
                  type="currency"
                  zero-value="-"
                  :value="row.dr_amount"
                />
              </div>
              <div class="col-3" data-testid="cr">
                <FormattedNumber
                  null-value="-"
                  type="currency"
                  zero-value="-"
                  :value="row.cr_amount"
                />
              </div>
            </div>
          </div>
          <div class="row text-bold q-mt-md bg-grey-3 q-pa-md items-center" style="margin-left: -20px; margin-right: -20px">
            <div class="col-grow">
              Sub Total
            </div>
            <div class="col-3">
              <FormattedNumber
                null-value="-"
                type="currency"
                :value="getAmount?.voucherTally[index].dr_amount"
              />
            </div>
            <div class="col-3">
              <FormattedNumber
                null-value="-"
                type="currency"
                :value="getAmount?.voucherTally[index].cr_amount"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-form>
    <q-card class="q-mt-sm q-mx-lg q-mb-xl">
      <q-card-section class="bg-grey-4">
        <div class="row text-bold">
          <div class="col-grow">
            Total
          </div>
          <div class="col-3" style="padding-left: 12px">
            <FormattedNumber
              v-if="sameTransactionsData"
              null-value="-"
              type="currency"
              :value="sameTransactionsData.total_dr"
            />
          </div>
          <div class="col-3" style="padding-left: 12px">
            <FormattedNumber
              v-if="sameTransactionsData"
              null-value="-"
              type="currency"
              :value="sameTransactionsData.total_cr"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </template>
  <template v-if="sameTransactionsData && fields?.length > 1">
    <div class="q-ma-md flex justify-end">
      <q-btn color="green" :label="separateTransactions ? 'View Merged Transactions' : 'View Separate Transactions'" @click="separateTransactions = !separateTransactions" />
    </div>
  </template>
</template>
