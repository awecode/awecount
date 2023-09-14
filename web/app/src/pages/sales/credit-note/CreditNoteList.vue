<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn color="blue" label="Exoprt Xls" icon-right="download" @click="onDownloadXls" />
      <q-btn v-if="checkPermissions('CreditNoteCreate')" color="green" to="/credit-note/add/" label="New Credit Note"
        class="q-ml-lg" icon-right="add" />
    </div>

    <q-table :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-ma-sm">
                    <MultiSelectChip :options="['Draft', 'Issued', 'Cancelled', 'Resolved']" v-model="filters.status" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props" class="row justify center">
          <q-btn v-if="checkPermissions('CreditNoteView')" color="blue" class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px" label="View" :to="`/credit-note/${props.row.id}/view`" />
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
            <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
              ? 'bg-blue-2 text-blue-9'
              : props.row.status == 'Resolved'
                ? 'bg-green-2 text-green-10'
                : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10' : 'bg-red-2 text-red-10'
              " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-party="props">
        <q-td :props="props">
          <div>
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party
            }}</span>
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import usedownloadFile from 'src/composables/usedownloadFile'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Credit Notes | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/credit-note/'
    const route = useRoute()
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('/v1/credit-note/export' + query)
        .then((data) =>
          usedownloadFile(
            data,
            'text/csv',
            'Credit_Notes'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), onDownloadXls, checkPermissions }
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
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
