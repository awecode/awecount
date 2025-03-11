<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const metaData = {
      title: 'Cheque Issues | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/cheque-issue/`
    const newColumn = [
      {
        name: 'issued_to',
        label: 'TO',
        align: 'left',
        field: 'issued_to',
        sortable: true,
      },
      {
        name: 'cheque_no',
        label: 'Cheque #',
        align: 'left',
        field: 'cheque_no',
        sortable: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: row => Math.round(row.amount * 100) / 100,
        sortable: true,
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true,
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/cheque-issue/export${query}`)
        //   // TODO: url not found
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Sales_voucher'))
        .catch(err => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumn, onDownloadXls, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="flex gap-4 justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export"
        @click="onDownloadXls"
      />
      <q-btn
        v-if="checkPermissions('chequeissue.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Cheque Issue"
        :to="`/${$route.params.company}/banking/cheque-issues/create`"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="full-width search-input"
            debounce="500"
            placeholder="Search"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-sm">
                    <n-auto-complete-v2
                      v-model="filters.bank_account"
                      label="Bank Account"
                      :endpoint="`/api/company/${$route.params.company}/bank-account/choices/`"
                      :fetch-on-mount="true"
                    />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Cleared']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn
                    class="f-submit-btn"
                    color="green"
                    label="Filter"
                    @click="onFilterUpdate"
                  />
                  <q-btn
                    class="f-reset-btn"
                    color="red"
                    icon="close"
                    @click="resetFilters"
                  />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-issued_to="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('chequeissue.update')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none"
            :to="`/${$route.params.company}/banking/cheque-issues/${props.row.id}/edit`"
          >
            {{ props.row.issued_to || props.row.party_name }}
          </router-link>
          <span v-else>{{ props.row.issued_to || props.row.party_name }}</span>
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Cleared' ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              "
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('chequeissue.update')"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="orange-6"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/banking/cheque-issues/${props.row.id}/edit`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
