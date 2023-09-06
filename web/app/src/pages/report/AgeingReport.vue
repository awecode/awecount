<template>
    <div class="q-pa-md">
        <div class="row q-gutter-x-md justify-end">
            <q-btn color="blue" label="Export XLS" icon-right="download" @click="onDownloadXls" />
        </div>
        {{ reportData }}
        <q-table title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
            v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
            <template v-slot:top>
                <div class="search-bar">
                    <!-- <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
                        <template v-slot:append>
                            <q-icon name="search" />
                        </template>
                    </q-input> -->
                    <div class="flex items-end q-gutter-md">
                        <DatePicker label="Date" v-model="filters.date"></DatePicker>
                        <q-btn color="green" label="Filter" class="q-mr-md" @click="onFilterUpdate"></q-btn>
                    </div>
                </div>
            </template>
            <!-- <template v-slot:body-cell-status="props">
                <q-td :props="props">
                    <div class="row align-center">
                        <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
                            ? 'bg-blue-2 text-blue-10'
                            : props.row.status == 'Resolved'
                                ? 'bg-green-2 text-green-10'
                                : props.row.status == 'Draft'
                                    ? 'bg-orange-2 text-orange-10'
                                    : 'bg-red-2 text-red-10'
                            " style="border-radius: 8px; padding: 2px 10px">
                            {{ props.row.status }}
                        </div>
                    </div>
                </q-td>
            </template>

            <template v-slot:body-cell-party_name="props">
                <q-td :props="props">
                    <div>
                        <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
                        <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
                            props.row.party
                        }}</span>
                    </div>
                </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                    <div class="row q-gutter-x-md items-center">
                        <q-btn color="blue" label="View" :to="`/debit-note/${props.row.id}/view/`"
                            class="q-py-none q-px-md font-size-sm" style="font-size: 12px" />
                    </div>
                </q-td>
            </template> -->
        </q-table>
    </div>
</template>


<script>
export default {
  setup() {
    const reportData= ref(null)
    const fields = ref({
      start_date: null,
      end_date: null,
    })
    const metaData = {
      title: 'Collection Report | Awecount',
    }
    useMeta(metaData)
    const fetchData = () => {
      const endpoint = `/v1/payment-receipt/collection-report/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => (reportData.value = data))
        .catch((err) => console.log(err))
      // TODO: add 404 error routing
    }
    return { reportData, fetchData, fields }
  },
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