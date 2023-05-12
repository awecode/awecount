<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-between q-gutter-x-md q-gutter-y-xs">
        <div class="flex items-center q-gutter-x-md q-gutter-y-xs">
          <div>
            <DateRangePicker v-model:startDate="fields.start_date" v-model:endDate="fields.end_date" :hide-btns="true" />
          </div>
          <q-btn v-if="fields.start_date || fields.end_date" color="red" icon="close"
            @click="fields = { start_date: null, end_date: null }"></q-btn>
          <q-btn :disable="!fields.start_date && !fields.end_date ? true : false" color="green" label="fetch"
            @click="fetchData"></q-btn>
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
    <div>
      <q-markup-table id="tableRef">
        <thead>
          <tr>
            <th class="text-left"><strong>Name</strong></th>
            <th class="text-left" :colspan="config.show_opening_closing_dr_cr ? '3' : '1'">
              Opening
            </th>
            <th class="text-left" colspan="2">Transactions</th>
            <th class="text-left" :colspan="config.show_opening_closing_dr_cr ? '3' : '1'">
              Closing
            </th>
          </tr>
          <tr>
            <th class="text-left"></th>
            <template v-if="config.show_opening_closing_dr_cr">
              <th class="text-left">Dr</th>
              <th class="text-left">Cr</th>
              <th class="text-left">Balance</th>
            </template>
            <th v-else class="text-left">Balance</th>
            <th class="text-left">Dr</th>
            <th class="text-left">Cr</th>
            <template v-if="config.show_opening_closing_dr_cr">
              <th class="text-left">Dr</th>
              <th class="text-left">Cr</th>
              <th class="text-left">Balance</th>
            </template>
            <th v-else class="text-left">Balance</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="showData">
            <TableNode v-for="category in categoryTree" :key="category.id" :item="category" :root="true"
              :accounts="accounts" :category_accounts="category_accounts" :config="config"></TableNode>
          </template>
          <tr>
            <td><span class="text-weight-medium">Total</span></td>
            <template v-if="config.show_opening_closing_dr_cr">
              <td class="text-left text-weight-medium">
                {{ total.opening_dr }}
              </td>
              <td class="text-left text-weight-medium">
                {{ total.opening_cr }}
              </td>
              <td class="text-left text-weight-medium">
                {{ calculateNet(total, 'opening') }}
              </td>
            </template>
            <td v-else class="text-left text-weight-medium">
              {{ calculateNet(total, 'opening') }}
            </td>
            <td class="text-left text-weight-medium">
              {{ parseFloat(total.transaction_dr.toFixed(2)) }}
            </td>
            <td class="text-left text-weight-medium">
              {{ parseFloat(total.transaction_cr.toFixed(2)) }}
            </td>
            <template v-if="config.show_opening_closing_dr_cr">
              <td class="text-left text-weight-medium">
                {{ parseFloat(total.closing_dr.toFixed(2)) }}
              </td>
              <td class="text-left text-weight-medium">
                {{ parseFloat(total.closing_cr.toFixed(2)) }}
              </td>
              <td class="text-left text-weight-medium">
                {{ calculateNet(total, 'closing') }}
              </td>
            </template>
            <td v-else class="text-left text-weight-medium">
              {{ calculateNet(total, 'closing') }}
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script>
// import { utils, writeFile } from 'xlsx'
import XLSX from "xlsx-js-style"
export default {
  setup() {
    const categoryTree = ref(null)
    const category_accounts = ref({})
    const config = ref({
      hide_accounts: false,
      hide_categories: false,
      hide_sums: false,
      show_opening_closing_dr_cr: false,
      hide_zero_transactions: false,
    })
    const accounts = ref({})
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

    // const endpoint = '/v1/trial-balance/'
    // const listData = useList(endpoint)
    const fetchData = () => {
      showData.value = false
      // const endpoint = `/v1/test/data/`
      const endpoint = `/v1/trial-balance/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => {
          category_accounts.value = {}
          accounts.value = {}
          let localAccounts = {}
          const tallyTotal = {
            transaction_dr: 0,
            transaction_cr: 0,
            opening_dr: 0,
            opening_cr: 0,
            closing_dr: 0,
            closing_cr: 0,
          }
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
            tallyTotal.transaction_dr += acc.transaction_dr
            tallyTotal.transaction_cr += acc.transaction_cr
            tallyTotal.opening_dr += acc.opening_dr
            tallyTotal.opening_cr += acc.opening_cr
            tallyTotal.closing_dr += acc.closing_dr
            tallyTotal.closing_cr += acc.closing_cr
            localAccounts[obj.id] = acc

            // Create this.category_accounts[obj.category_id] if doesn't exist
            !(obj.category_id in category_accounts.value) &&
              (category_accounts.value[obj.category_id] = [])
            category_accounts.value[obj.category_id].push(obj.id)
          })
          // TODO make unreactive
          accounts.value = localAccounts
          showData.value = true
          total.value = tallyTotal
        })
        .catch((err) => console.log(err))
      // TODO: add 404 error routing
    }
    // functions
    // const onDownloadXls = () => {
    //   // TODO: add download xls link
    //   const elt = document.getElementById('tableRef').children[0]
    //   const baseUrl = window.location.origin
    //   replaceHrefAttribute(elt, baseUrl)
    //   const wb = utils.table_to_book(elt, {
    //     sheet: 'sheet1',
    //   })
    //   writeFileXLSX(wb, 'TrialBalance.xls')
    // }
    const onDownloadXls = () => {
      // TODO: add download xls link
      const elt = document.getElementById('tableRef').children[0]
      const baseUrl = window.location.origin
      replaceHrefAttribute(elt, baseUrl)
      // adding styles
      const worksheet = XLSX.utils.table_to_sheet(elt)
      for (const i in worksheet) {
        if (typeof (worksheet[i]) != 'object') continue
        let cell = XLSX.utils.decode_cell(i)
        worksheet[i].s = {
          font: { name: 'Courier', sz: 12 }
        }
        if (cell.c == 0 || cell.r == 0 || cell.r == 1) { // first clumn || first and sec row
          worksheet[i].s.font.bold = true
          // worksheet[i].s.font.color = { rgb: '1976d2' }
          // debugger
          if (cell.r != 0 && cell.r != 1) {
            worksheet[i].s.font.color = { rgb: '1976d2' }
          }
        }
        // debugger
        if (cell.r == worksheet[`!rows`].length) {
          // worksheet[i].s.font.bold = true
        }
        if (cell.r == (worksheet[`!rows`].length - 1)) {
          worksheet[i].s.border = { top: { style: 'thin', color: { rgb: '000000' } } }
        }
      }
      const workbook = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(workbook, worksheet, 'sheet_name_here');
      const excelBuffer = XLSX.write(workbook, {
        type: 'buffer',
        cellStyles: true,
      });
      // download Excel
      XLSX.writeFileXLSX(workbook, 'TrialBalance.xls')
    }
    // to replace link '/' with base url
    const replaceHrefAttribute = (element, baseUrl) => {
      if (!element || !element.childNodes) return
      for (var i = 0; i < element.childNodes.length; i++) {
        var child = element.childNodes[i]
        if (child.tagName === 'A') {
          const link = child.getAttribute('href')
          child.setAttribute('href', baseUrl + `${link}`)
        }
        replaceHrefAttribute(child, baseUrl)
      }
    }
    return {
      replaceHrefAttribute,
      onDownloadXls,
      fields,
      fetchData,
      total,
      categoryTree,
      accounts,
      category_accounts,
      showData,
      config,
      calculateNet,
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
