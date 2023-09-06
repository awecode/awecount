<template>
    <div class="q-pa-md">
        <div class="row q-gutter-x-md justify-end">
            <q-btn color="blue" label="Export XLS" icon-right="download" @click="onDownloadXls" />
        </div>
        <q-table title="Income Items" :rows="reportData" :columns="newColumns" :loading="loading" row-key="id"
            @request="onRequest" class="q-mt-md" hide-bottom>
            <template v-slot:top>
                <div class="search-bar">
                    <!-- <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
                        <template v-slot:append>
                            <q-icon name="search" />
                        </template>
                    </q-input> -->
                    <div class="flex items-end q-gutter-md">
                        <DatePicker label="Date" v-model="date"></DatePicker>
                        <q-btn color="green" label="Filter" class="q-mr-md" @click="fetchData"></q-btn>
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
export default {
    setup() {
        const route = useRoute()
        const reportData = ref([])
        const loading = ref(false)
        // const 
        const date = ref(route.query.date || null)
        const metaData = {
            title: 'Customer Ageing Report | Awecount',
        }
        useMeta(metaData)
        const fetchData = () => {
            const endpoint = `/v1/report/ageing-report/?date=${date.value}`
            loading.value = true
            useApi(endpoint)
                .then((data) => {
                    reportData.value = data
                    loading.value = false
                })
                .catch((err) => {
                    console.log(err)
                    loading.value = false
                })
            // TODO: add 404 error routing
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
        return { reportData, fetchData, date, newColumns, checkPermissions }
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