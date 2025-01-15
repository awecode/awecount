<script>
import { useLoginStore } from 'src/stores/login-info'
// import { utils, writeFile } from 'xlsx'
// import XLSX from "xlsx-js-style"
import { useRoute } from 'vue-router'

export default {
  setup() {
    const categoryTree = ref(null)
    const category_accounts = ref({})
    const route = useRoute()
    const loginStore = useLoginStore()
    const config = ref({
      hide_accounts: false,
      hide_sums: false,
      show_opening_closing_dr_cr: false,
    })
    const objFormat = {
      transaction_dr: 0,
      transaction_cr: 0,
      opening_dr: 0,
      opening_cr: 0,
      closing_dr: 0,
      closing_cr: 0,
    }
    const showData = ref(false)
    const total = ref(null)
    const computedTreeData = ref(null)
    const unCatogarizedData = ref([])
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
      const filedArray = ['transaction_dr', 'transaction_cr', 'opening_dr', 'opening_cr', 'closing_dr', 'closing_cr']
      const endpoint = `/api/company/${route.params.company}/inventory-account/trial-balance/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => {
          unCatogarizedData.value = []
          const categoryData = JSON.stringify(categoryTree.value)
          const computedData = [...JSON.parse(categoryData)]
          const tallyTotal = { ...objFormat }
          data.forEach((obj) => {
            const acc = {
              account_id: obj.id,
              name: obj.name,
              category_id: obj.item__category_id,
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
            const index = categoryTree.value.findIndex(item => item.id === acc.category_id)
            if (index > -1) {
              if (!computedData[index]?.children) {
                computedData[index].children = []
                computedData[index].total = { ...objFormat }
              }
              computedData[index].children.push(acc)
              filedArray.forEach((field_name) => {
                computedData[index].total[field_name] += acc[field_name]
              })
            } else {
              unCatogarizedData.value.push(acc)
            }
          })
          // TODO make unreactive
          computedTreeData.value = computedData
          showData.value = true
          total.value = tallyTotal
        })
        .catch(err => console.log(err))
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
      //     type: 'buffer',
      //     cellStyles: true,
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
    const changeExpandStatus = (id) => {
      const index = loginStore.stockTrialBalanceCollapseId.indexOf(id)
      if (index >= 0) loginStore.stockTrialBalanceCollapseId.splice(index, 1)
      else loginStore.stockTrialBalanceCollapseId.push(id)
    }

    const endpoint = `/api/company/${route.params.company}/inventory-categories/trial-balance/`
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
      categoryTree,
      category_accounts,
      showData,
      config,
      calculateNet,
      route,
      objFormat,
      total,
      computedTreeData,
      changeExpandStatus,
      loginStore,
      unCatogarizedData,
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
            @click="fetchData"
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
                    <q-checkbox v-model="config.hide_sums" label="Hide Sums?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.show_opening_closing_dr_cr" label="Show Opening Closing Dr/Cr?" />
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
            <template v-for="parent in computedTreeData" :key="parent.id">
              <template v-if="parent.children && parent.children.length > 0">
                <tr>
                  <td class="text-blue-6 text-weight-bold">
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                    <span style="display: inline-block; width: 40px; margin-left: -5px">
                      <q-btn
                        dense
                        flat
                        round
                        class="expand-btn"
                        :class="loginStore.stockTrialBalanceCollapseId.includes(parent.id) ? '' : 'expanded'"
                        @click="changeExpandStatus(parent.id)"
                      >
                        <svg
                          class="text-grey-7"
                          height="32"
                          viewBox="0 0 24 24"
                          width="32"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" fill="currentColor" />
                        </svg>
                      </q-btn>
                    </span>
                    <RouterLink
                      class="text-blue-6"
                      style="text-decoration: none"
                      target="_blank"
                      :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${parent.id}`"
                    >
                      {{ parent.name }}
                    </RouterLink>
                  </td>
                  <template v-if="config.show_opening_closing_dr_cr">
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ parent.total?.opening_dr }}</span>
                    </td>
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ parent.total?.opening_cr }}</span>
                    </td>
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ calculateNet(parent.total, 'opening') }}</span>
                    </td>
                  </template>
                  <td v-else class="text-left text-weight-medium">
                    <span v-if="!config.hide_sums">{{ calculateNet(parent.total, 'opening') }}</span>
                  </td>
                  <td class="text-left text-weight-medium">
                    <span v-if="!config.hide_sums">{{ parseFloat(parent.total.transaction_dr.toFixed(2)) }}</span>
                  </td>
                  <td class="text-left text-weight-medium">
                    <span v-if="!config.hide_sums">{{ parseFloat(parent.total.transaction_cr.toFixed(2)) }}</span>
                  </td>
                  <template v-if="config.show_opening_closing_dr_cr">
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ parseFloat(parent.total.closing_dr.toFixed(2)) }}</span>
                    </td>
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ parseFloat(parent.total.closing_cr.toFixed(2)) }}</span>
                    </td>
                    <td class="text-left text-weight-medium">
                      <span v-if="!config.hide_sums">{{ calculateNet(parent.total, 'closing') }}</span>
                    </td>
                  </template>
                  <td v-else class="text-left text-weight-medium">
                    <span v-if="!config.hide_sums">{{ calculateNet(parent.total, 'closing') }}</span>
                  </td>
                </tr>
                <template v-for="(child, index) in parent.children" :key="index">
                  <tr v-if="!loginStore.stockTrialBalanceCollapseId.includes(parent.id) && !config.hide_accounts">
                    <td class="text-blue-6">
                      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                      <span style="display: inline-block; width: 40px; margin-left: -5px"></span>
                      <RouterLink
                        class="text-blue-6"
                        style="text-decoration: none"
                        target="_blank"
                        :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${child.account_id}`"
                      >
                        {{ child.name }}
                      </RouterLink>
                    </td>
                    <template v-if="config.show_opening_closing_dr_cr">
                      <td class="text-left text-weight-medium">
                        {{ child.opening_dr }}
                      </td>
                      <td class="text-left text-weight-medium">
                        {{ child.opening_cr }}
                      </td>
                      <td class="text-left text-weight-medium">
                        {{ calculateNet(child, 'opening') }}
                      </td>
                    </template>
                    <td v-else class="text-left text-weight-medium">
                      {{ calculateNet(child, 'opening') }}
                    </td>
                    <td class="text-left text-weight-medium">
                      {{ parseFloat(child.transaction_dr.toFixed(2)) }}
                    </td>
                    <td class="text-left text-weight-medium">
                      {{ parseFloat(child.transaction_cr.toFixed(2)) }}
                    </td>
                    <template v-if="config.show_opening_closing_dr_cr">
                      <td class="text-left text-weight-medium">
                        {{ parseFloat(child.closing_dr.toFixed(2)) }}
                      </td>
                      <td class="text-left text-weight-medium">
                        {{ parseFloat(child.closing_cr.toFixed(2)) }}
                      </td>
                      <td class="text-left text-weight-medium">
                        {{ calculateNet(child, 'closing') }}
                      </td>
                    </template>
                    <td v-else class="text-left text-weight-medium">
                      {{ calculateNet(child, 'closing') }}
                    </td>
                  </tr>
                </template>
              </template>
            </template>
            <template v-for="child in unCatogarizedData" :key="child.account_id">
              <tr v-if="!config.hide_accounts">
                <td class="text-blue-6">
                  <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                  <RouterLink
                    class="text-blue-6"
                    style="text-decoration: none"
                    target="_blank"
                    :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${child.account_id}`"
                  >
                    {{ child.name }}
                  </RouterLink>
                </td>
                <template v-if="config.show_opening_closing_dr_cr">
                  <td class="text-left text-weight-medium">
                    {{ child.opening_dr }}
                  </td>
                  <td class="text-left text-weight-medium">
                    {{ child.opening_cr }}
                  </td>
                  <td class="text-left text-weight-medium">
                    {{ calculateNet(child, 'opening') }}
                  </td>
                </template>
                <td v-else class="text-left text-weight-medium">
                  {{ calculateNet(child, 'opening') }}
                </td>
                <td class="text-left text-weight-medium">
                  {{ parseFloat(child.transaction_dr.toFixed(2)) }}
                </td>
                <td class="text-left text-weight-medium">
                  {{ parseFloat(child.transaction_cr.toFixed(2)) }}
                </td>
                <template v-if="config.show_opening_closing_dr_cr">
                  <td class="text-left text-weight-medium">
                    {{ parseFloat(child.closing_dr.toFixed(2)) }}
                  </td>
                  <td class="text-left text-weight-medium">
                    {{ parseFloat(child.closing_cr.toFixed(2)) }}
                  </td>
                  <td class="text-left text-weight-medium">
                    {{ calculateNet(child, 'closing') }}
                  </td>
                </template>
                <td v-else class="text-left text-weight-medium">
                  {{ calculateNet(child, 'closing') }}
                </td>
              </tr>
            </template>
            <tr v-if="showData">
              <td class="text-weight-medium">
                <span>Total</span>
              </td>
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
          </template>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>
