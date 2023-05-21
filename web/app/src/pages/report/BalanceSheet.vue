<template>
    <div class="q-pa-md">
        <div class="q-px-md q-pb-md">
            <div class="flex items-center justify-between q-gutter-x-md q-gutter-y-xs">
                <div class="flex items-center q-gutter-x-md q-gutter-y-xs">
                    <div>
                        <!-- <DateRangePicker v-model:startDate="fields.start_date" v-model:endDate="fields.end_date"
                            :hide-btns="true" /> -->
                    </div>
                    <q-btn v-if="fields.start_date || fields.end_date" color="red" icon="close"
                        @click="fields = { start_date: null, end_date: null }"></q-btn>
                    <q-btn :disable="!fields.start_date && !fields.end_date ? true : false" color="green" label="fetch"
                        @click="onAddColumn"></q-btn>
                </div>
                <div class="flex q-gutter-x-md q-gutter-y-xs" v-if="showData">
                    <q-btn class="filterbtn" icon="settings" title="Config">
                        <q-menu>
                            <div class="menu-wrapper" style="width: min(300px, 90vw)">
                                <div style="border-bottom: 1px solid lightgrey">
                                    <h6 class="q-ma-md text-grey-9">Config</h6>
                                </div>
                                <div class="q-ma-sm">
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_accounts" label="Hide Accounts?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_categories" label="Hide Categories?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_sums" label="Hide Sums?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.show_opening_closing_dr_cr"
                                            label="Show Opening Closing Dr/Cr?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_zero_transactions"
                                            label="Hide accounts without transactions?"></q-checkbox>
                                    </div>
                                </div>
                            </div>
                        </q-menu>
                    </q-btn>
                    <q-btn color="green" label="Export Xls" icon-right="download" @click="onDownloadXls" />
                </div>
            </div>
        </div>
        <div class="flex q-gutter-x-sm">
            <q-markup-table id="tableRef">
                <thead>
                    <tr>
                        <th class="text-left" style="width: 400px;"><strong>Name</strong></th>
                        <th class="text-left" style="width: 400px;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-if="showData">
                        <BalanceSheetTableNode :item="categoryTree[0]" :root="true" :accounts="accounts" :isAsset=true
                            :category_accounts="category_accounts" :config="config">
                        </BalanceSheetTableNode>
                        <BalanceSheetTableNode :item="categoryTree[1]" :root="true" :accounts="accounts"
                            :category_accounts="category_accounts" :config="config">
                        </BalanceSheetTableNode>
                        <BalanceSheetTableNode :item="categoryTree[4]" :root="true" :accounts="accounts"
                            :category_accounts="category_accounts" :config="config">
                        </BalanceSheetTableNode>
                    </template>
                    <tr>
                        <td class="text-weight-medium"><span>Total</span></td>
                        <td>ahsvhasv</td>
                    </tr>
                </tbody>
            </q-markup-table>
            <div>
                <q-btn color="green" icon="add" class="m-none q-pa-sm">
                    <q-menu>
                        <div class="menu-wrapper" style="width: min(300px, 90vw)">
                            <div style="border-bottom: 1px solid lightgrey">
                                <h6 class="q-ma-md text-grey-9">Add Column</h6>
                            </div>
                            <div class="q-mx-md row q-gutter-md q-mt-xs q-mb-md">
                                <DateRangePicker v-model:startDate="secondfields.start_date"
                                    v-model:endDate="secondfields.end_date" :hide-btns="true" />
                                <q-btn color="green" label="Filter" @click="onAddColumn"></q-btn>
                                <q-btn color="red" icon="close"
                                    @click="secondfields = { start_date: null, end_date: null }"></q-btn>
                            </div>
                        </div>
                    </q-menu>
                </q-btn>
            </div>
        </div>
    </div>
</template>
  
<script>
// import { utils, writeFile } from 'xlsx'
// import XLSX from "xlsx-js-style"
export default {
    setup() {
        const categoryTree = ref(null)
        const category_accounts = ref([])
        const config = ref({
            hide_accounts: false,
            hide_categories: false,
            hide_sums: false,
            show_opening_closing_dr_cr: false,
            hide_zero_transactions: false,
        })
        const accounts = ref([])
        const showData = ref(false)
        const total = ref({
            transaction_dr: 0,
            transaction_cr: 0,
            opening_dr: 0,
            opening_cr: 0,
            closing_dr: 0,
            closing_cr: 0,
        })
        const fields = ref({
            start_date: null,
            end_date: null,
        })
        const calculateNet = (obj, type) => {
            const net = parseFloat(
                (obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2)
            )
            if (net === 0) {
                return 0
            } else if (net > 0) {
                return `${net}` + ' cr'
            } else {
                return `${net * -1}` + ' dr'
            }
        }
        const secondfields = ref({
            start_date: null,
            end_date: null,
        })
        // const endpoint = '/v1/trial-balance/'
        // const listData = useList(endpoint)
        const fetchData = async (start_date, end_date, index) => {
            showData.value = false
            // const endpoint = `/v1/test/data/`
            const endpoint = `/v1/trial-balance/?start_date=${start_date}&end_date=${end_date}`
            let data = null
            try {
                data = await useApi(endpoint)
            }
            catch (error) {
                console.log(error)
            }
            // accounts.value = {}
            let localAccounts = {}
            category_accounts.value[index] = []
            data.forEach((obj) => {
                const acc = {
                    account_id: obj.id,
                    name: obj.name,
                    category_id: obj.category_id,
                    opening_dr: obj.od || 0,
                    opening_cr: obj.oc || 0,
                    closing_dr: obj.cd || 0,
                    closing_cr: obj.cc || 0,
                    transaction_dr: (obj.cd || 0) - (obj.od || 0),
                    transaction_cr: (obj.cc || 0) - (obj.oc || 0),
                }
                localAccounts[obj.id] = acc
                // Create this.category_accounts[obj.category_id] if doesn't exist
                !(obj.category_id in category_accounts.value[index]) &&
                    (category_accounts.value[index][obj.category_id] = [])
                category_accounts.value[index][obj.category_id].push(obj.id)
            })
            // debugger
            accounts.value[index] = localAccounts
            showData.value = true
        }
        // const onDownloadXls = () => {
        //     // TODO: add download xls link
        //     const elt = document.getElementById('tableRef').children[0]
        //     const baseUrl = window.location.origin
        //     replaceHrefAttribute(elt, baseUrl)
        //     // adding styles
        //     const worksheet = XLSX.utils.table_to_sheet(elt)
        //     for (const i in worksheet) {
        //         if (typeof (worksheet[i]) != 'object') continue
        //         let cell = XLSX.utils.decode_cell(i)
        //         worksheet[i].s = {
        //             font: { name: 'Courier', sz: 12 }
        //         }
        //         if (cell.r == 0) { // first row
        //             worksheet[i].s.font.bold = true
        //         }
        //         if (cell.c == 0) { // first row
        //             const td = elt.rows[cell.r].cells[cell.c]
        //             worksheet[i].s.font.italic = getComputedStyle(td).fontStyle === 'italic'
        //             //get color and apply to excel
        //             const hexCode = getComputedStyle(td).color
        //             const hexArray = hexCode.slice(4, hexCode.length - 1).split(',')
        //             const numsArray = hexArray.map((e) => Number(e))
        //             const rgbValue = (1 << 24 | numsArray[0] << 16 | numsArray[1] << 8 | numsArray[2]).toString(16).slice(1)
        //             worksheet[i].s.font.color = { rgb: `${rgbValue}` }
        //         }
        //         if (cell.r > -1) {
        //             const td = elt.rows[cell.r].cells[cell.c]
        //             if (td instanceof HTMLElement) worksheet[i].s.font.bold = Number(getComputedStyle(td).fontWeight) >= 500
        //         }
        //     }
        //     worksheet['!cols'] = [{ width: 50 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 },]
        //     const workbook = XLSX.utils.book_new()
        //     XLSX.utils.book_append_sheet(workbook, worksheet, 'sheet_name_here');
        //     const excelBuffer = XLSX.write(workbook, {
        //         type: 'buffer',
        //         cellStyles: true,
        //     });
        //     // download Excel
        //     XLSX.writeFileXLSX(workbook, 'TrialBalance.xls')
        // }
        // // to replace link '/' with base url
        // const replaceHrefAttribute = (element, baseUrl) => {
        //     if (!element || !element.childNodes) return
        //     for (var i = 0; i < element.childNodes.length; i++) {
        //         var child = element.childNodes[i]
        //         if (child.tagName === 'A') {
        //             const link = child.getAttribute('href')
        //             child.setAttribute('href', baseUrl + `${link}`)
        //         }
        //         replaceHrefAttribute(child, baseUrl)
        //     }
        // }
        const onAddColumn = () => {
            const data = fetchData(secondfields.value.start_date, secondfields.value.end_date, 0)
            // console.log('do something')
        }
        return {
            fields,
            fetchData,
            total,
            categoryTree,
            accounts,
            category_accounts,
            showData,
            config,
            calculateNet,
            secondfields,
            onAddColumn
        }
    },
    created() {
        const endpoint = '/v1/category-tree/'
        useApi(endpoint, { method: 'GET' })
            .then((data) => {
                this.categoryTree = data
            })
            .catch((error) => {
                console.log('err fetching data', error)
            })
    },
}
</script>
  
  <!-- <style scoped>
  .q-table thead tr,
  .q-table tbody td {
    height: 20px !important;
    background-color: black !important;
  }
  </style> -->
  