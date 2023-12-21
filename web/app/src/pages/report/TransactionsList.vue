<template>
    <div class="q-pa-md">
        <div class="row q-gutter-x-md justify-end">
            <q-btn color="blue" label="Export" icon-right="download" @click="onDownloadXls" />
        </div>
        <q-table :rows="rows" :columns="rows[0]?.label ? newColumnTwo : newColumn" :loading="loading" :filter="searchQuery"
            v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
            <template v-slot:top>
                <div class="search-bar">
                    <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
                        <template v-slot:append>
                            <q-icon name="search" />
                        </template>
                    </q-input>
                    <q-btn class="filterbtn" icon="mdi-filter-variant">
                        <q-menu>
                            <div class="menu-wrapper" style="width: min(550px, 90vw); height: min(700px, 60vh)">
                                <div style="border-bottom: 1px solid lightgrey">
                                    <h6 class="q-ma-md text-grey-9">Filters</h6>
                                </div>
                                <div class="q-ma-md">
                                    <FiltersOptions v-model="filters.account" label="Account"
                                        :options="filterOptions.collections?.accounts" />
                                    <FiltersOptions v-model="filters.source" label="Transaction Type"
                                        :options="filterOptions.collections?.transaction_types" />
                                    <FiltersOptions v-model="filters.category" label="Category"
                                        :options="filterOptions.collections?.categories" />

                                    <div>
                                        <h5 class="text-subtitle2 text-grey-8">Group By:</h5>
                                        <div>
                                            <q-select v-model="filters.group" :label="`Group By`" option-value="id"
                                                option-label="name" :options="groupByOption" map-options emit-value>
                                                <template v-slot:append>
                                                    <q-icon v-if="filters.group !== null" class="cursor-pointer"
                                                        name="clear"
                                                        @click.stop.prevent="filters.group = null" /></template>
                                            </q-select>
                                        </div>
                                    </div>
                                    <!-- {{ filterOptions.collections.accounts }} -->
                                </div>
                                <div class="q-mx-md">
                                    <DateRangePicker v-model:startDate="filters.start_date"
                                        v-model:endDate="filters.end_date" />
                                </div>
                                <div class="q-mx-md row q-pb-md q-mt-lg">
                                    <q-btn color="green" label="Filter" class="q-mr-md" @click="onFilterUpdate"></q-btn>
                                    <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                                </div>
                            </div>
                        </q-menu>
                    </q-btn>
                </div>
            </template>
            <template v-slot:body-cell-account="props">
                <q-td :props="props">
                    <RouterLink style="text-decoration: none" target="_blank"
                        :to="`/account/?has_balance=true&category=${props.row.category_id}`" class="text-blue-6">{{
                            props.row.account_name
                        }}
                    </RouterLink>
                </q-td>
            </template>
            <template v-slot:body-cell-type="props">
                <q-td :props="props">
                    <RouterLink v-if="checkPermissions(getPermissionsWithSourceType[props.row.source_type])" style="
                        text-decoration: none" target="_blank" :to="getVoucherUrl(props.row)" class="text-blue-6">{{
                            props.row.source_type
                        }}
                    </RouterLink>
                    <span v-else> {{ props.row.source_type }}</span>
                </q-td>
            </template>
        </q-table>
        <!-- <q-card class="q-pa-md q-mt-md">
            <PieChart :data="ratioData.chart_data" />
        </q-card> -->
    </div>
</template>
  
<script>
import useList from '/src/composables/useList'
// import usedownloadFile from 'src/composables/usedownloadFile'
import DateRangePicker from 'src/components/date/DateRangePicker.vue'
import checkPermissions from 'src/composables/checkPermissions'
// import { useMeta } from 'quasar'
export default {
    setup() {
        const metaData = {
            title: 'Sales Invoices | Awecount',
        }
        const groupByOption = [
            {
                id: 'acc',
                name: 'Account'
            },
            {
                id: 'cat',
                name: 'Category'
            },
            {
                id: 'type',
                name: 'Transaction Type'
            }
        ]
        const filterOptions = ref({})
        useMeta(metaData)
        const endpoint = '/v1/transaction/'
        const listData = useList(endpoint)
        const route = useRoute()
        const onDownloadXls = () => {
            const query = route.fullPath.slice(route.fullPath.indexOf('?'))
            useApi('v1/transaction/export' + query)
                .then((data) =>
                    usedownloadFile(
                        data,
                        'application/vnd.ms-excel',
                        'Sales_voucher'
                    )
                )
                .catch((err) => console.log('Error Due To', err))
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
            if (source_type === 'Sales Voucher')
                return `/sales-voucher/${row.source_id}/view/`
            if (source_type === 'Purchase Voucher')
                return `/purchase-voucher/${row.source_id}/view`
            if (source_type === 'Journal Voucher')
                return `/journal-voucher/${row.source_id}/view`
            if (source_type === 'Credit Note')
                return `/credit-note/${row.source_id}/view`
            if (source_type === 'Debit Note')
                return `/debit-note/${row.source_id}/view`
            // if (source_type === 'Tax Payment') return 'Tax Payment Edit'
            // TODO: add missing links
            if (source_type === 'Cheque Deposit')
                return `/cheque-deposit/${row.source_id}/view/`
            if (source_type === 'Payment Receipt')
                return `/payment-receipt/${row.source_id}/view/`
            if (source_type === 'Cheque Issue')
                return `/cheque-issue/${row.source_id}/`
            if (source_type === 'Challan') return `/challan/${row.source_id}/`
            if (source_type === 'Account Opening Balance')
                return `/account-opening-balance/${row.source_id}/`
            if (source_type === 'Item') return `/items/details/${row.source_id}/`
            // added
            if (source_type === 'Fund Transfer')
                return `/bank/fund/fund-transfer/${row.source_id}/edit/`
            if (source_type === 'Bank Cash Deposit')
                return `/bank/cash/cash-deposit/${row.source_id}/edit/`
            if (source_type === 'Tax Payment') return `/tax-payment/${row.source_id}/`
            console.error(source_type + ' not handled!')
        }
        const getPermissionsWithSourceType = {
            'Sales Voucher': 'SalesView',
            'Purchase Voucher': 'PurchaseVoucherView',
            'Journal Voucher': 'JournalVoucherView',
            'Credit Note': 'CreditNoteView',
            'Debit Note': 'DebitNoteView',
            'Cheque Deposit': 'ChequeDepositView',
            'Payment Receipt': 'PaymentReceiptView',
            'Cheque Issue': 'ChequeIssueModify',
            'Challan': 'ChallanModify',
            'Account Opening Balance': 'AccountOpeningBalanceModify',
            'Fund Transfer': 'FundTransferModify',
            'Bank Cash Deposit': 'BankCashDepositModify',
            'Tax Payment': 'TaxPaymentModify',
            'Item': 'ItemView'
        }
        // const chartData = computed(() => {
        //     if (listData.rows.value[0]?.label) {
        //         console.log(listData.rows.value)
        //         return true
        //     }
        //     else return null
        // })
        return { ...listData, newColumn, newColumnTwo, getVoucherUrl, filterOptions, groupByOption, onDownloadXls, getPermissionsWithSourceType, checkPermissions }
    },
    created() {
        const endpoint = '/v1/transaction/create-defaults/'
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
    width: 80px;
    flex-grow: 0;
    flex-shrink: 0;
}
</style>
  