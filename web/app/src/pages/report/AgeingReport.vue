<script>
import { withQuery } from 'ufo'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const reportData = ref([])
    const loading = ref(false)
    const pagination = ref(null)
    const date = ref(route.query.date || null)
    const metaData = {
      title: 'Customer Ageing Report | Awecount',
    }
    useMeta(metaData)

    // Initialize date if not set
    if (!date.value) {
      const now = new Date().toISOString().substring(0, 10)
      const routeObj = {
        path: route.path,
        query: {
          date: now,
        },
      }
      date.value = now
      router.push(routeObj)
    }

    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/report/export-ageing-report/${query}`)
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Customer_Ageing_Report'))
        .catch(err => console.log('Error Due To', err))
    }

    function onRequest(props) {
      let url = route.path
      if (props.pagination.page == 1) {
        url = withQuery(url, { page: undefined })
      } else {
        url = withQuery(url, { page: props.pagination.page })
      }
      if (route.query.date) {
        url = withQuery(url, { date: route.query.date })
      }
      router.push(url)
      fetchData()
    }

    function onUpdate() {
      let url = route.path
      if (route.query.page == 1) {
        url = withQuery(url, { page: undefined })
      } else {
        url = withQuery(url, { page: route.query.page })
      }
      if (date.value) {
        url = withQuery(url, { date: date.value })
      }
      router.push(url)
      fetchData()
    }

    const newColumns = [
      {
        name: 'party',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      {
        name: 'total',
        label: 'Net Due',
        align: 'left',
        field: 'grand_total',
      },
      { name: 'total_30', label: '30 Days', align: 'left', field: 'total_30' },
      { name: 'total_60', label: '60 Days', align: 'left', field: 'total_60' },
      { name: 'total_90', label: '90 Days', align: 'left', field: 'total_90' },
      { name: 'total_120', label: '120 Days', align: 'left', field: 'total_120' },
      { name: 'total_120plus', label: '120 Days Plus', align: 'left', field: 'total_120plus' },
    ]

    const fetchData = () => {
      const endpoint = `/api/company/${route.params.company}/report/ageing-report/?date=${date.value}${route.query.page ? `&page=${route.query.page}` : ''}`
      loading.value = true
      useApi(endpoint)
        .then((data) => {
          reportData.value = data.results
          loading.value = false
          pagination.value = {
            page: data.pagination.page,
            rowsPerPage: data.pagination.size,
            rowsNumber: data.pagination.count,
          }
        })
        .catch((err) => {
          console.log(err)
          loading.value = false
          pagination.value = null
        })
    }

    // Initial data fetch
    fetchData()

    return {
      reportData,
      fetchData,
      date,
      newColumns,
      checkPermissions,
      pagination,
      onRequest,
      onUpdate,
      onDownloadXls,
      loading,
    }
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
        label="Export XLS"
        @click="onDownloadXls"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Income Items"
      :columns="newColumns"
      :loading="loading"
      :rows="reportData"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="flex items-end gap-6">
          <DatePicker v-model="date" label="Date" />
          <q-btn
            class="q-mr-md f-submit-btn"
            color="green"
            label="Filter"
            @click="onUpdate"
          />
        </div>
      </template>
      <template #body-cell-party="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('category.modify')"
            class="text-blue l-view-btn"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/crm/parties/${props.row.party_id}/account`"
          >
            {{ props.row.party_name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.party_name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
