<template>
    <div class="q-pa-md">
        <div class="row q-gutter-x-md justify-end">
            <q-btn color="blue" label="Export" icon-right="download" @click="onDownloadXls" />
        </div>
        <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
            row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
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
                                    <!-- {{ filterOptions.collections.accounts }} -->
                                    <!-- <div class="q-mb-sm">
                                        <q-checkbox v-model="filters.is_due" label="Is Due?"
                                            :false-value="null"></q-checkbox>
                                    </div>
                                    <div class="q-ma-sm">
                                        <MultiSelectChip :options="[
                                            'Draft',
                                            'Issued',
                                            'Paid',
                                            'Partially Paid',
                                            'Cancelled',
                                        ]" v-model="filters.status" />
                                    </div> -->
                                </div>
                                <div class="q-mx-md">
                                    <DateRangePicker v-model:startDate="filters.start_date"
                                        v-model:endDate="filters.end_date" />
                                </div>
                                <div class="q-mx-md row q-mb-md q-mt-lg">
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
                        :to="`/account/?has_balance=true&category=${props.row.account_id}`" class="text-blue-6">{{
                            props.row.account_name
                        }}
                    </RouterLink>
                </q-td>
            </template>
            <template v-slot:body-cell-type="props">
                <q-td :props="props">
                    <RouterLink style="text-decoration: none" target="_blank" :to="getVoucherUrl(props.row)"
                        class="text-blue-6">{{
                            props.row.source_type
                        }}
                    </RouterLink>
                </q-td>
            </template>
        </q-table>
    </div>
</template>
  
<script>
import useList from '/src/composables/useList'
// import usedownloadFile from 'src/composables/usedownloadFile'
import MultiSelectChip from 'src/components/filter/MultiSelectChip.vue'
import DateRangePicker from 'src/components/date/DateRangePicker.vue'
// import { useMeta } from 'quasar'
export default {
    setup() {
        const metaData = {
            title: 'Sales Invoices | Awecount',
        }
        const filterOptions = ref({})
        useMeta(metaData)
        const endpoint = '/v1/transaction/'
        const listData = useList(endpoint)
        const route = useRoute()
        // const onDownloadXls = () => {
        //     const query = route.fullPath.slice(route.fullPath.indexOf('?'))
        //     useApi('v1/sales-voucher/export/' + query)
        //         .then((data) =>
        //             usedownloadFile(
        //                 data,
        //                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        //                 'Sales_voucher'
        //             )
        //         )
        //         .catch((err) => console.log('Error Due To', err))
        // }
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
            // {
            //     name: 'type',
            //     label: 'Type',
            //     align: 'left',
            //     field: 'source_type',
            // },
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
                return `/bank/cheque/cheque-deposit/${row.source_id}/view/`
            if (source_type === 'Payment Receipt')
                return `/payment-receipt/${row.source_id}/view/`
            if (source_type === 'Cheque Issue')
                return `/bank/cheque/cheque-issue/${row.source_id}/edit/`
            if (source_type === 'Challan') return `/challan/${row.source_id}/`
            if (source_type === 'Account Opening Balance')
                return `/account/opening-balance/${row.source_id}/edit/`
            if (source_type === 'Item') return `/items/opening/${row.source_id}`
            // added
            if (source_type === 'Fund Transfer')
                return `/bank/fund/fund-transfer/${row.source_id}/edit/`
            if (source_type === 'Bank Cash Deposit')
                return `/bank/cash/cash-deposit/${row.source_id}/edit/`
            if (source_type === 'Tax Payment') return `/tax-payment/${row.source_id}/`
            console.error(source_type + ' not handled!')
        }
        return { ...listData, newColumn, getVoucherUrl, filterOptions }
    },
    created() {
        const endpoint = '/v1/transaction/create-defaults/'
        useApi(endpoint, { method: 'GET' })
            .then((data) => {
                console.log(data)
                this.filterOptions = data
            })
            .catch((error) => {
                if (error.response && error.response.status == 404) {
                    this.$router.replace({ name: '404' })
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
  