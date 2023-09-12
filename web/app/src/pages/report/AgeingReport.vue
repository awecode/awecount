<template>
    <div class="q-pa-md">
        <div class="row q-gutter-x-md justify-end">
            <q-btn color="blue" label="Export XLS" icon-right="download" @click="onDownloadXls" />
        </div>
        <q-table title="Income Items" :rows="reportData" :columns="newColumns" :loading="loading" row-key="id"
            @request="onRequest" v-model:pagination="pagination" class="q-mt-md" :rows-per-page-options="[20]">
            <template v-slot:top>
                <div class="search-bar">
                    <!-- <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
                        <template v-slot:append>
                            <q-icon name="search" />
                        </template>
                    </q-input> -->
                    <div class="flex items-end q-gutter-md">
                        <DatePicker label="Date" v-model="date"></DatePicker>
                        <q-btn color="green" label="Filter" class="q-mr-md" @click="onUpdate"></q-btn>
                    </div>
                </div>
            </template>
            <template v-slot:body-cell-party="props">
                <q-td :props="props">
                    <router-link v-if="checkPermissions('CategoryModify')" style="font-weight: 500; text-decoration: none"
                        class="text-blue" :to="`/parties/account/${props.row.party_id}/`">{{ props.row.party_name
                        }}</router-link>
                    <span v-else>{{ props.row.party_name }}</span>
                </q-td>
            </template>
        </q-table>
    </div>
</template>


<script>
import checkPermissions from 'src/composables/checkPermissions'
import { withQuery } from 'ufo'
export default {
    setup() {
        const route = useRoute()
        const router = useRouter()
        const reportData = ref([])
        const loading = ref(false)
        const pagination = ref(null)
        // const 
        const date = ref(route.query.date || null)
        const metaData = {
            title: 'Customer Ageing Report | Awecount',
        }
        useMeta(metaData)
        const onDownloadXls = () => {
            const query = route.fullPath.slice(route.fullPath.indexOf('?'))
            useApi('v1/report/export-ageing-report/' + query)
                .then((data) =>
                    usedownloadFile(
                        data,
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'Customer_Ageing_Report'
                    )
                )
                .catch((err) => console.log('Error Due To', err))
        }
        const fetchData = () => {
            const endpoint = `/v1/report/ageing-report/?date=${date.value}${route.query.page ? `&page=${route.query.page}` : ''}`
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
            // TODO: add 404 error routing
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
            { name: 'total_120plus', label: '120 Days Plus', align: 'left', field: 'total_120plus' }
        ]
        // watch(() => route.query, () => {
        //     fetchData()
        // })
        return { reportData, fetchData, date, newColumns, checkPermissions, pagination, onRequest, onUpdate, onDownloadXls }
    },
    created() {
        if (!this.date) {
            const now = new Date().toISOString().substring(0, 10)
            const routeObj = {
                path: this.$route.path,
                query: {
                    date: now
                }
            }
            this.date = now
            this.$router.push(routeObj)
            // route.query
        }
        this.fetchData()
    }
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
    width: min(300px, 90%);
    flex-grow: 0;
    flex-shrink: 0;
}
</style>