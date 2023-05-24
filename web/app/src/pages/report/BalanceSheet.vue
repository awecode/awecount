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
            let data = [
                {
                    "id": 7785,
                    "name": "TDS Receivables",
                    "category_id": 497,
                    "od": null,
                    "oc": null,
                    "cd": 22.95,
                    "cc": null
                },
                {
                    "id": 7786,
                    "name": "Cash",
                    "category_id": 498,
                    "od": 10000,
                    "oc": 5000,
                    "cd": 17401.5,
                    "cc": 5045.2
                },
                {
                    "id": 7799,
                    "name": "Opening Balance Difference",
                    "category_id": 490,
                    "od": 1,
                    "oc": 11000,
                    "cd": 1,
                    "cc": 11000
                },
                {
                    "id": 11251,
                    "name": "Pencils (Purchase)",
                    "category_id": 518,
                    "od": null,
                    "oc": null,
                    "cd": 100000,
                    "cc": 100000
                },
                {
                    "id": 11253,
                    "name": "Discount Allowed - banner",
                    "category_id": 529,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 2
                },
                {
                    "id": 11254,
                    "name": "banner (Purchase)",
                    "category_id": 518,
                    "od": 4000,
                    "oc": null,
                    "cd": 4000,
                    "cc": null
                },
                {
                    "id": 11256,
                    "name": "abcd (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 920.95,
                    "cc": 139.95
                },
                {
                    "id": 11257,
                    "name": "abcd (Payable)",
                    "category_id": 505,
                    "od": 20000,
                    "oc": null,
                    "cd": 20000,
                    "cc": null
                },
                {
                    "id": 11258,
                    "name": "tds Receivable",
                    "category_id": 497,
                    "od": null,
                    "oc": null,
                    "cd": 5020,
                    "cc": 5000
                },
                {
                    "id": 11261,
                    "name": "Discount Received - name",
                    "category_id": 517,
                    "od": null,
                    "oc": null,
                    "cd": 10,
                    "cc": null
                },
                {
                    "id": 11262,
                    "name": "Furniture",
                    "category_id": 493,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 10
                },
                {
                    "id": 11263,
                    "name": "abcd",
                    "category_id": 491,
                    "od": null,
                    "oc": 1,
                    "cd": 2,
                    "cc": 1
                },
                {
                    "id": 11264,
                    "name": "bank",
                    "category_id": 485,
                    "od": 1000,
                    "oc": null,
                    "cd": 1000,
                    "cc": null
                },
                {
                    "id": 11265,
                    "name": "cash",
                    "category_id": 485,
                    "od": 2000,
                    "oc": null,
                    "cd": 2000,
                    "cc": null
                },
                {
                    "id": 11266,
                    "name": "name",
                    "category_id": 491,
                    "od": null,
                    "oc": 2000,
                    "cd": null,
                    "cc": 2000
                },
                {
                    "id": 11267,
                    "name": "Stationary",
                    "category_id": 485,
                    "od": 5000,
                    "oc": null,
                    "cd": 5000,
                    "cc": null
                },
                {
                    "id": 11268,
                    "name": "SCB (09000198765457)",
                    "category_id": 500,
                    "od": null,
                    "oc": 30000,
                    "cd": 23,
                    "cc": 31245
                },
                {
                    "id": 11269,
                    "name": "NMB (09099998888)",
                    "category_id": 500,
                    "od": null,
                    "oc": null,
                    "cd": 6935.225,
                    "cc": 10000
                },
                {
                    "id": 11270,
                    "name": "edusanjal (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 123
                },
                {
                    "id": 11276,
                    "name": "txt",
                    "category_id": 485,
                    "od": null,
                    "oc": 4000,
                    "cd": null,
                    "cc": 4000
                },
                {
                    "id": 16731,
                    "name": "TAX Payable",
                    "category_id": 512,
                    "od": null,
                    "oc": null,
                    "cd": 1250.2,
                    "cc": 1103.7
                },
                {
                    "id": 16736,
                    "name": "Cotton Masks (Sales)",
                    "category_id": 513,
                    "od": null,
                    "oc": null,
                    "cd": 40,
                    "cc": 540
                },
                {
                    "id": 16737,
                    "name": "Discount Allowed - Cotton Masks",
                    "category_id": 517,
                    "od": null,
                    "oc": null,
                    "cd": 50,
                    "cc": null
                },
                {
                    "id": 16740,
                    "name": "Siddhartha Industries (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 2170.278,
                    "cc": 5000
                },
                {
                    "id": 16741,
                    "name": "Siddhartha Industries (Payable)",
                    "category_id": 505,
                    "od": null,
                    "oc": null,
                    "cd": 10000,
                    "cc": 5420
                },
                {
                    "id": 16742,
                    "name": "Helmet - Red (Sales)",
                    "category_id": 513,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 8000
                },
                {
                    "id": 16744,
                    "name": "Helmet - Red (Purchase)",
                    "category_id": 518,
                    "od": null,
                    "oc": null,
                    "cd": 400,
                    "cc": null
                },
                {
                    "id": 16746,
                    "name": "NIBL",
                    "category_id": 500,
                    "od": null,
                    "oc": null,
                    "cd": 5000,
                    "cc": null
                },
                {
                    "id": 18028,
                    "name": "asd",
                    "category_id": 500,
                    "od": null,
                    "oc": null,
                    "cd": 16.725,
                    "cc": 23
                },
                {
                    "id": 18135,
                    "name": "Value Added Tax Payable",
                    "category_id": 512,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 409.578
                },
                {
                    "id": 18136,
                    "name": "Pencils (Sales)",
                    "category_id": 513,
                    "od": null,
                    "oc": null,
                    "cd": null,
                    "cc": 3345
                },
                {
                    "id": 18137,
                    "name": "Discount Allowed - Pencils",
                    "category_id": 517,
                    "od": null,
                    "oc": null,
                    "cd": 194.4,
                    "cc": null
                },
                {
                    "id": 18139,
                    "name": "Rohan (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 1711.95,
                    "cc": 1711.95
                },
                {
                    "id": 18140,
                    "name": "Rohan (Payable)",
                    "category_id": 505,
                    "od": null,
                    "oc": null,
                    "cd": 105000,
                    "cc": 105000
                },
                {
                    "id": 18229,
                    "name": "ashuja (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 920.95,
                    "cc": null
                },
                {
                    "id": 18255,
                    "name": "ABC (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 16.95,
                    "cc": null
                },
                {
                    "id": 18261,
                    "name": "asmalsm (Receivable)",
                    "category_id": 502,
                    "od": null,
                    "oc": null,
                    "cd": 11.3,
                    "cc": null
                }
            ]
            // try {
            //     data = await useApi(endpoint)
            // }
            // catch (error) {
            //     console.log(error)
            // }
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
            console.log('localAccounts', localAccounts)
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
        this.categoryTree = [
            {
                "id": 485,
                "name": "Assets",
                "children": [
                    {
                        "id": 491,
                        "name": "Other Receivables",
                        "children": []
                    },
                    {
                        "id": 492,
                        "name": "Deferred Assets",
                        "children": []
                    },
                    {
                        "id": 493,
                        "name": "Fixed Assets",
                        "children": []
                    },
                    {
                        "id": 497,
                        "name": "Tax Receivables",
                        "children": []
                    },
                    {
                        "id": 498,
                        "name": "Cash Accounts",
                        "children": []
                    },
                    {
                        "id": 500,
                        "name": "Bank Accounts",
                        "children": []
                    },
                    {
                        "id": 501,
                        "name": "Account Receivables",
                        "children": [
                            {
                                "id": 502,
                                "name": "Customers",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": 486,
                "name": "Liabilities",
                "children": [
                    {
                        "id": 504,
                        "name": "Account Payables",
                        "children": [
                            {
                                "id": 505,
                                "name": "Suppliers",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": 506,
                        "name": "Other Payables",
                        "children": []
                    },
                    {
                        "id": 512,
                        "name": "Duties & Taxes",
                        "children": []
                    }
                ]
            },
            {
                "id": 487,
                "name": "Income",
                "children": [
                    {
                        "id": 513,
                        "name": "Sales",
                        "children": []
                    },
                    {
                        "id": 514,
                        "name": "Direct Income",
                        "children": []
                    },
                    {
                        "id": 516,
                        "name": "Indirect Income",
                        "children": [
                            {
                                "id": 517,
                                "name": "Discount Income",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": 488,
                "name": "Expenses",
                "children": [
                    {
                        "id": 518,
                        "name": "Purchase",
                        "children": []
                    },
                    {
                        "id": 519,
                        "name": "Direct Expenses",
                        "children": []
                    },
                    {
                        "id": 521,
                        "name": "Indirect Expenses",
                        "children": [
                            {
                                "id": 528,
                                "name": "Fuel and Transport",
                                "children": []
                            },
                            {
                                "id": 529,
                                "name": "Discount Expenses",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": 489,
                "name": "Equity",
                "children": []
            },
            {
                "id": 490,
                "name": "Opening Balance Difference",
                "children": []
            }
        ]
        // useApi(endpoint, { method: 'GET' })
        //     .then((data) => {
        //         this.categoryTree = data
        //     })
        //     .catch((error) => {
        //         console.log('err fetching data', error)
        //     })
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
  