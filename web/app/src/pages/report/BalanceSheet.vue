<script>
// import { utils, writeFile } from 'xlsx'
import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

export default {
  setup() {
    const route = useRoute()
    const store = useLoginStore()
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
    const timePeriodArray = ref([])
    const calculateNet = (obj, type) => {
      const net = Number.parseFloat((obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2))
      if (net === 0) {
        return 0
      } else if (net > 0) {
        return `${net}` + ' cr'
      } else {
        return `${net * -1}` + ' dr'
      }
    }
    // const secondfields = ref({
    //     start_date: null,
    //     end_date: null,
    // })
    // const endpoint = '/api/company/trial-balance/'
    // const listData = useList(endpoint)
    const fetchData = async (start_date, end_date, index) => {
      showData.value = false
      // const endpoint = `/api/company/test/data/`
      const endpoint = `/api/company/${route.params.company}/trial-balance/?start_date=${start_date}&end_date=${end_date}`
      let data = null
      try {
        data = await useApi(endpoint)
      } catch (error) {
        console.log(error)
      }
      // accounts.value = {}
      const localAccounts = {}
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
        !(obj.category_id in category_accounts.value[index]) && (category_accounts.value[index][obj.category_id] = [])
        category_accounts.value[index][obj.category_id].push(obj.id)
      })
      accounts.value[index] = localAccounts
      showData.value = true
    }
    const onDownloadXls = async () => {
      // TODO: add download xls link
      const XLSX = await import('xlsx-js-style')
      const elt = document.getElementById('tableRef').children[0]
      const baseUrl = window.location.origin
      replaceHrefAttribute(elt, baseUrl)
      // adding styles
      const worksheet = XLSX.utils.table_to_sheet(elt)
      for (const i in worksheet) {
        if (typeof worksheet[i] != 'object') continue
        const cell = XLSX.utils.decode_cell(i)
        worksheet[i].s = {
          font: { name: 'Courier', sz: 12 },
        }
        if (cell.r == 0) {
          // first row
          worksheet[i].s.font.bold = true
        }
        if (cell.c == 0) {
          // first row
          const td = elt.rows[cell.r].cells[cell.c]
          worksheet[i].s.font.italic = getComputedStyle(td).fontStyle === 'italic'
          // get color and apply to excel
          const hexCode = getComputedStyle(td).color
          const hexArray = hexCode.slice(4, hexCode.length - 1).split(',')
          const numsArray = hexArray.map((e) => Number(e))
          const rgbValue = ((1 << 24) | (numsArray[0] << 16) | (numsArray[1] << 8) | numsArray[2]).toString(16).slice(1)
          worksheet[i].s.font.color = { rgb: `${rgbValue}` }
        }
        if (cell.r > -1) {
          const td = elt.rows[cell.r].cells[cell.c]
          if (td instanceof HTMLElement) worksheet[i].s.font.bold = Number(getComputedStyle(td).fontWeight) >= 500
        }
      }
      worksheet['!cols'] = [{ width: 50 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }, { width: 16 }]
      const workbook = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(workbook, worksheet, 'sheet_name_here')
      // download Excel
      XLSX.writeFileXLSX(workbook, 'TrialBalance.xls')
    }
    // to replace link '/' with base url
    const replaceHrefAttribute = (element, baseUrl) => {
      if (!element || !element.childNodes) return
      for (let i = 0; i < element.childNodes.length; i++) {
        const child = element.childNodes[i]
        if (child.tagName === 'A') {
          const link = child.getAttribute('href')
          child.setAttribute('href', `${baseUrl}${link}`)
        }
        replaceHrefAttribute(child, baseUrl)
      }
    }
    const onAddColumn = () => {
      // const addIndex = accounts.value.length ? accounts.value.length : 0
      // const data = fetchData(fields.value.start_date, fields.value.end_date, addIndex)
      timePeriodArray.value.push({ ...fields.value })
    }
    const onRemoveColumn = (index) => {
      if (accounts.value.length === 1) {
        category_accounts.value = []
        accounts.value = []
        showData.value = false
        timePeriodArray.value = []
      } else {
        accounts.value.splice(index, 1)
        category_accounts.value.splice(index, 1)
        timePeriodArray.value.splice(index, 1)
      }
    }

    const endpoint = `/api/company/${route.params.company}/category-tree/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        categoryTree.value = data
      })
      .catch((error) => {
        console.log('err fetching data', error)
      })

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
      onAddColumn,
      onRemoveColumn,
      onDownloadXls,
      timePeriodArray,
      store,
      DateConverter,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-end q-gutter-x-md q-gutter-y-xs">
        <!-- <div class="flex items-center q-gutter-x-md q-gutter-y-xs">
                    <div>
                    </div>
                    <q-btn v-if="fields.start_date || fields.end_date" color="red" icon="close"
                        @click="fields = { start_date: null, end_date: null }"></q-btn>
                    <q-btn :disable="!fields.start_date && !fields.end_date ? true : false" color="green" label="fetch"
                        @click="onAddColumn"></q-btn>
                </div> -->
        <div v-if="showData" class="flex q-gutter-x-md q-gutter-y-xs">
          <q-btn class="filterbtn" icon="settings" title="Config">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Config</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_accounts" label="Hide Accounts?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_categories" label="Hide Categories?" />
                  </div>
                  <!-- <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_sums" label="Hide Sums?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.show_opening_closing_dr_cr"
                                            label="Show Opening Closing Dr/Cr?"></q-checkbox>
                                    </div>
                                    <div class="q-pb-sm">
                                        <q-checkbox v-model="config.hide_zero_transactions"
                                            label="Hide accounts without transactions?"></q-checkbox>
                                    </div> -->
                </div>
              </div>
            </q-menu>
          </q-btn>
          <q-btn color="green" label="Export Xls" icon-right="download" @click="onDownloadXls" />
        </div>
      </div>
    </div>
    <div class="flex q-gutter-x-sm flex no-wrap">
      <div class="col-grow" style="max-width: calc(100% - 50px)">
        <q-markup-table id="tableRef">
          <thead>
            <tr v-if="showData" class="bg-grey-2">
              <th class="text-weight-medium text-caption text-left">
                <span class="q-pl-lg">Time Period</span>
              </th>
              <th v-for="(timeperoid, index) in timePeriodArray" :key="index">
                <!-- {{ timeperoid }} -->
                <div class="flex">
                  <div class="text-weight-medium text-caption text-left">
                    <div style="margin-bottom: -5px">{{ store.isCalendarInAD ? timeperoid.start_date : DateConverter.getRepresentation(timeperoid.start_date, 'bs') }}&nbsp;</div>
                    <div>{{ store.isCalendarInAD ? timeperoid.end_date : DateConverter.getRepresentation(timeperoid.end_date, 'bs') }}</div>
                  </div>
                  <q-btn v-if="accounts.length > 0" dense flat color="red-5" size="sm" title="Delete Column" class="q-ml-md" @click="onRemoveColumn(index)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12Z" />
                    </svg>
                  </q-btn>
                </div>
              </th>
              <!-- <td v-for=""></td> -->
            </tr>
            <tr>
              <th class="text-left" style="width: 400px">
                <strong :class="showData ? 'q-ml-lg' : ''">Name</strong>
              </th>
              <th v-for="(account, index) in accounts.length || 1" :key="index" class="text-left" style="width: 400px">
                <div class="flex items-center">
                  <span class="q-mr-md text-weight-bold">Amount</span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-if="showData">
              <BalanceSheetTableNode :item="categoryTree[0]" :root="true" :accounts="accounts" :is-asset="true" :category_accounts="category_accounts" :config="config" />
              <BalanceSheetTableNode :item="categoryTree[1]" :root="true" :accounts="accounts" :category_accounts="category_accounts" :config="config" />
              <BalanceSheetTableNode :item="categoryTree[4]" :root="true" :accounts="accounts" :category_accounts="category_accounts" :config="config" />
            </template>
            <tr v-if="!showData">
              <td class="text-weight-medium">
                <span>Total</span>
              </td>
              <td>0</td>
            </tr>
          </tbody>
        </q-markup-table>
      </div>
      <div style="width: 30px">
        <q-btn color="green" icon="add" class="m-none q-pa-sm" title="Add Column">
          <q-menu>
            <div class="menu-wrapper" style="width: min(300px, 90vw)">
              <div style="border-bottom: 1px solid lightgrey">
                <h6 class="q-ma-md text-grey-9">Add Column</h6>
              </div>
              <div class="q-mx-md row q-gutter-md q-mt-xs q-mb-md">
                <DateRangePicker v-model:start-date="fields.start_date" v-model:end-date="fields.end_date" :hide-btns="true" />
                <q-btn color="green" label="Filter" @click="onAddColumn" />
                <q-btn color="red" icon="close" @click="fields = { start_date: null, end_date: null }" />
              </div>
            </div>
          </q-menu>
        </q-btn>
      </div>
    </div>
  </div>
</template>

<!-- <style scoped>
  .q-table thead tr,
  .q-table tbody td {
    height: 20px !important;
    background-color: black !important;
  }
  </style> -->
