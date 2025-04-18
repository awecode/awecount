<script>
import checkPermissions from '@/composables/checkPermissions'
import useList from '@/composables/useList'

export default {
  setup() {
    const metaData = {
      title: 'Sales Invoices | Awecount',
    }
    const groupByOption = [
      {
        id: 'acc',
        name: 'Account',
      },
      {
        id: 'cat',
        name: 'Category',
      },
      {
        id: 'type',
        name: 'Transaction Type',
      },
    ]
    const filterOptions = ref({})
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/transaction/`
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/transaction/export${query}`)
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Sales_voucher'))
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Voucher no',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      {
        name: 'account',
        label: 'Account',
        align: 'left',
        field: 'account_name',
      },
      {
        name: 'type',
        label: 'Type',
        align: 'left',
        field: 'source_type',
      },
      {
        name: 'dr',
        label: 'Dr',
        align: 'left',
        field: 'dr_amount',
      },
      {
        name: 'cr',
        label: 'CR',
        align: 'left',
        field: 'cr_amount',
      },
    ]
    const newColumnTwo = [
      {
        name: 'label',
        label: 'Name',
        align: 'left',
        field: 'label',
      },
      {
        name: 'year',
        label: 'Year',
        align: 'left',
        field: 'year',
      },
      {
        name: 'total_debit',
        label: 'Dr',
        align: 'left',
        field: 'total_debit',
      },
      {
        name: 'cr',
        label: 'CR',
        align: 'left',
        field: 'total_credit',
      },
    ]
    function getVoucherUrl(row) {
      const source_type = row.source_type
      if (source_type === 'Sales Voucher') {
        return `/${route.params.company}/sales/vouchers/${row.source_id}`
      }
      if (source_type === 'Purchase Voucher') {
        return `/${route.params.company}/purchase/vouchers/${row.source_id}`
      }
      if (source_type === 'Journal Voucher') {
        return `/${route.params.company}/account/journal-vouchers/${row.source_id}`
      }
      if (source_type === 'Credit Note') {
        return `/${route.params.company}/sales/credit-notes/${row.source_id}`
      }
      if (source_type === 'Debit Note') {
        return `/${route.params.company}/purchase/debit-notes/${row.source_id}`
      }
      if (source_type === 'Challan') {
        return `/${route.params.company}/sales/challans/${row.source_id}`
      }
      if (source_type === 'Cheque Deposit') {
        return `/${route.params.company}/banking/cheque-deposit/${row.source_id}`
      }
      if (source_type === 'Payment Receipt') {
        return `/${route.params.company}/payment-receipts/${row.source_id}`
      }
      if (source_type === 'Cheque Issue') {
        return `/${route.params.company}/banking/cheque-issue/${row.source_id}/edit`
      }
      if (source_type === 'Account Opening Balance') {
        return `/${route.params.company}/account/opening-balances/${row.source_id}/edit`
      }
      if (source_type === 'Fund Transfer') {
        return `/${route.params.company}/banking/fund-transfers/${row.source_id}/edit`
      }
      if (source_type === 'Bank Cash Deposit') {
        return `/${route.params.company}/banking/cash-deposit/${row.source_id}/edit`
      }
      if (source_type === 'Tax Payment') {
        return `/${route.params.company}/tax/payments/${row.source_id}/edit`
      }
      if (source_type === 'Inventory Adjustment Voucher') {
        return `/${route.params.company}/inventory/adjustments/${row.source_id}`
      }
      console.error(`${source_type} not handled!`)
    }
    const getPermissionsWithSourceType = {
      'Account Opening Balance': 'accountopeningbalance.update',
      'Bank Cash Deposit': 'bankcashdeposit.update',
      'Challan': 'challan.update',
      'Cheque Deposit': 'chequedeposit.read',
      'Cheque Issue': 'chequeissue.update',
      'Credit Note': 'creditnote.read',
      'Debit Note': 'debitnote.read',
      'Fund Transfer': 'fundtransfer.update',
      'Inventory Adjustment Voucher': 'inventoryadjustmentvoucher.read',
      'Item': 'item.read',
      'Journal Voucher': 'journalvoucher.read',
      'Payment Receipt': 'paymentreceipt.read',
      'Purchase Voucher': 'purchasevoucher.read',
      'Sales Voucher': 'sales.read',
      'Tax Payment': 'taxpayment.update',
    }
    return { ...listData, newColumn, newColumnTwo, getVoucherUrl, filterOptions, groupByOption, onDownloadXls, getPermissionsWithSourceType, checkPermissions }
  },
  created() {
    const endpoint = `/api/company/${this.$route.params.company}/transaction/create-defaults/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.filterOptions = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export"
        @click="onDownloadXls"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="rows[0]?.label ? newColumnTwo : newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="full-width search-input"
            debounce="500"
            placeholder="Search"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw); height: min(700px, 60vh)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-md">
                  <FiltersOptions
                    v-model="filters.account"
                    label="Account"
                    :endpoint="`/api/company/${$route.params.company}/accounts/choices`"
                    :fetch-on-mount="true"
                    :options="filterOptions.collections?.accounts"
                  />
                  <FiltersOptions
                    v-model="filters.source"
                    label="Transaction Type"
                    :endpoint="`/api/company/${$route.params.company}/transaction/create-defaults/transaction_types`"
                    :options="filterOptions.collections?.transaction_types"
                  />
                  <FiltersOptions
                    v-model="filters.category"
                    label="Category"
                    :endpoint="`/api/company/${$route.params.company}/categories/choices`"
                    :fetch-on-mount="true"
                    :options="filterOptions.collections?.categories"
                  />

                  <div>
                    <h5 class="text-subtitle2 text-grey-8">
                      Group By:
                    </h5>
                    <div>
                      <q-select
                        v-model="filters.group"
                        emit-value
                        map-options
                        label="Group By"
                        option-label="name"
                        option-value="id"
                        :options="groupByOption"
                      >
                        <template #append>
                          <q-icon
                            v-if="filters.group !== null"
                            class="cursor-pointer"
                            name="clear"
                            @click.stop.prevent="filters.group = null"
                          />
                        </template>
                      </q-select>
                    </div>
                  </div>
                  <!-- {{ filterOptions.collections.accounts }} -->
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                </div>
                <div class="q-mx-md row q-pb-md q-mt-lg">
                  <q-btn
                    class="q-mr-md f-submit-btn"
                    color="green"
                    label="Filter"
                    @click="onFilterUpdate"
                  />
                  <q-btn
                    class="f-reset-btn"
                    color="red"
                    icon="close"
                    @click="resetFilters"
                  />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <RouterLink
            v-if="checkPermissions(getPermissionsWithSourceType[props.row.source_type]) && getVoucherUrl(props.row)"
            class="text-blue-6"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            target="_blank"
            :to="getVoucherUrl(props.row)"
          >
            {{ props.row.voucher_no }}
          </RouterLink>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.voucher_no }}
          </span>
        </q-td>
      </template>
      <template #body-cell-account="props">
        <q-td style="padding: 0" :props="props">
          <RouterLink
            class="text-blue-6"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            target="_blank"
            :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${props.row.category_id}`"
          >
            {{ props.row.account_name }}
          </RouterLink>
        </q-td>
      </template>
      <template #body-cell-type="props">
        <q-td style="padding: 0" :props="props">
          <RouterLink
            v-if="checkPermissions(getPermissionsWithSourceType[props.row.source_type]) && getVoucherUrl(props.row)"
            class="text-blue-6"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            target="_blank"
            :to="getVoucherUrl(props.row)"
          >
            {{ props.row.source_type }}
          </RouterLink>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.source_type }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
