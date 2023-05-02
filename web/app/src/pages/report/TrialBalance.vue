<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="green"
        label="Export Xls"
        icon-right="download"
        @click="onDownloadXls"
      />
    </div>
    <div class="q-px-md">
      <div class="flex items-center q-gutter-md">
        <div class="q-mx-md">
          <DateRangePicker
            v-model:startDate="fields.start_date"
            v-model:endDate="fields.end_date"
            :hide-btns="true"
          />
        </div>
        <q-btn
          v-if="fields.start_date || fields.end_date"
          color="red"
          icon="close"
          @click="fields = { start_date: null, end_date: null }"
        ></q-btn>
        <q-btn
          :disable="!fields.start_date && !fields.end_date ? true : false"
          color="green"
          label="fetch"
          @click="fetchData"
        ></q-btn>
        <q-btn class="filterbtn" icon="settings" title="Config"></q-btn>
      </div>
    </div>
    <div>
      <q-markup-table>
        <thead>
          <tr>
            <th class="text-left">Name</th>
            <th class="text-left">Opening</th>
            <th class="text-center" colspan="2">Transactions</th>
            <th class="text-left">Closing</th>
          </tr>
          <tr>
            <th class="text-left"></th>
            <th class="text-left">Balance</th>
            <th class="text-left">Dr</th>
            <th class="text-left">Cr</th>
            <th class="text-left">Balance</th>
          </tr>
        </thead>
        <tbody>
          <!-- <tr>
            <td class="text-left">Frozen Yogurt</td>
            <td class="text-left">159</td>
            <td class="text-left">6</td>
            <td class="text-left">24</td>
            <td class="text-left">4</td>
          </tr> -->
          <template v-if="true">
            <TableNode
              v-for="category in categoryTree"
              :key="category.id"
              :item="category"
              :root="true"
              :accounts="accounts"
              :category_accounts="category_accounts"
            ></TableNode>
          </template>
        </tbody>
      </q-markup-table>
    </div>
  </div>
  {{ category_accounts }} --category_accounts
</template>

<script>
export default {
  setup() {
    const categoryTree = ref(null)
    const category_accounts = ref({})
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
    // const endpoint = '/v1/trial-balance/'
    // const listData = useList(endpoint)
    const fetchData = () => {
      showData.value = false
      const endpoint = `/v1/test/data/`
      // const endpoint = `/v1/trial-balance/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => {
          category_accounts.value = {}
          accounts.value = {}
          let localAccounts = {}
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
            total.transaction_dr += acc.transaction_dr
            total.transaction_cr += acc.transaction_cr
            total.opening_dr += acc.opening_dr
            total.opening_cr += acc.opening_cr
            total.closing_dr += acc.closing_dr
            total.closing_cr += acc.closing_cr
            localAccounts[obj.id] = acc

            // Create this.category_accounts[obj.category_id] if doesn't exist
            !(obj.category_id in category_accounts.value) &&
              (category_accounts.value[obj.category_id] = [])
            category_accounts.value[obj.category_id].push(obj.id)
          })
          // TODO make unreactive
          accounts.value = localAccounts
          showData.value = true
        })
        .catch((err) => console.log(err))
      // TODO: add 404 error routing
    }
    // functions
    const onDownloadXls = () => {
      // TODO: add download xls link
      useApi('v1/sales-voucher/export/')
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Credit_Notes'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return {
      onDownloadXls,
      fields,
      fetchData,
      total,
      categoryTree,
      accounts,
      category_accounts,
      showData,
    }
  },
  created() {
    const endpoint = '/v1/test/category-tree/'
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
