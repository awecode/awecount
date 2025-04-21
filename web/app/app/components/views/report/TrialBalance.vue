<script>
// import { utils, writeFile } from 'xlsx'
// import XLSX from "xlsx-js-style"
export default {
  setup() {
    useHead({
      title: 'Trial Balance | Awecount',
    })
    const categoryTree = ref(null)
    const category_accounts = ref({})
    const route = useRoute()
    const router = useRouter()
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
      const net = Number.parseFloat((obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2))
      if (net === 0) {
        return 0
      } else if (net > 0) {
        return `${net}` + ' cr'
      } else {
        return `${net * -1}` + ' dr'
      }
    }

    // const endpoint = '/api/company/trial-balance/'
    // const listData = useList(endpoint)
    const fetchData = () => {
      showData.value = false
      // const endpoint = `/api/company/test/data/`
      const endpoint = `/api/company/${route.params.company}/trial-balance/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => {
          category_accounts.value = {}
          accounts.value = {}
          const localAccounts = {}
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
            !(obj.category_id in category_accounts.value) && (category_accounts.value[obj.category_id] = [])
            category_accounts.value[obj.category_id].push(obj.id)
          })
          // TODO make unreactive
          accounts.value = localAccounts
          showData.value = true
          total.value = tallyTotal
        })
        .catch(err => console.log(err))
      // TODO: add 404 error routing
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
          const numsArray = hexArray.map(e => Number(e))
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
      // const excelBuffer = XLSX.write(workbook, {
      //   type: 'buffer',
      //   cellStyles: true,
      // });
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
    function updateData() {
      const query = { ...fields.value }
      router.push({ path: `/${route.params.company}/reports/trial-balance/`, query })
      fetchData()
    }
    if (route.query.start_date && route.query.end_date) {
      fields.value.start_date = route.query.start_date
      fields.value.end_date = route.query.end_date
      fetchData()
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
      updateData,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-between gap-2">
        <div class="flex gap-x-6 gap-y-2 items-center">
          <div>
            <DateRangePicker
              v-model:end-date="fields.end_date"
              v-model:start-date="fields.start_date"
              :focus-on-mount="true"
              :hide-btns="true"
            />
          </div>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            class="f-reset-btn"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
          />
          <q-btn
            class="f-submit-btn"
            color="green"
            label="fetch"
            :disable="!fields.start_date && !fields.end_date ? true : false"
            @click="updateData"
          />
        </div>
        <div v-if="showData" class="flex gap-6">
          <q-btn icon="settings" title="Config">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Config
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_accounts" label="Hide Accounts?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_categories" label="Hide Categories?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_sums" label="Hide Sums?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.show_opening_closing_dr_cr" label="Show Opening Closing Dr/Cr?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_zero_transactions" label="Hide accounts without transactions?" />
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
          <q-btn
            class="export-btn"
            color="blue"
            icon-right="download"
            label="Export Xls"
            @click="onDownloadXls"
          />
        </div>
      </div>
    </div>
    <div>
      <q-markup-table id="tableRef">
        <thead>
          <tr>
            <th class="text-left">
              <strong>Name</strong>
            </th>
            <th class="text-left" :colspan="config.show_opening_closing_dr_cr ? '3' : '1'">
              Opening
            </th>
            <th class="text-left" colspan="2">
              Transactions
            </th>
            <th class="text-left" :colspan="config.show_opening_closing_dr_cr ? '3' : '1'">
              Closing
            </th>
          </tr>
          <tr>
            <th class="text-left"></th>
            <template v-if="config.show_opening_closing_dr_cr">
              <th class="text-left">
                Dr
              </th>
              <th class="text-left">
                Cr
              </th>
              <th class="text-left">
                Balance
              </th>
            </template>
            <th v-else class="text-left">
              Balance
            </th>
            <th class="text-left">
              Dr
            </th>
            <th class="text-left">
              Cr
            </th>
            <template v-if="config.show_opening_closing_dr_cr">
              <th class="text-left">
                Dr
              </th>
              <th class="text-left">
                Cr
              </th>
              <th class="text-left">
                Balance
              </th>
            </template>
            <th v-else class="text-left">
              Balance
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-if="showData">
            <TableNode
              v-for="category in categoryTree"
              :key="category.id"
              :accounts="accounts"
              :category_accounts="category_accounts"
              :config="config"
              :item="category"
              :root="true"
            />
          </template>
          <tr>
            <td class="text-weight-medium">
              <span>Total</span>
            </td>
            <template v-if="config.show_opening_closing_dr_cr">
              <td class="text-left text-weight-medium">
                {{ parseFloat(total.opening_dr.toFixed(2)) }}
              </td>
              <td class="text-left text-weight-medium">
                {{ parseFloat(total.opening_cr.toFixed(2)) }}
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
