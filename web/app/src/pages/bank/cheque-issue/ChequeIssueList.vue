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
      useApi(`v1/${route.params.company}/cheque-issue/export${query}`)
        //   // TODO: url not found
        .then(data =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Sales_voucher',
          ),
        )
        .catch(err => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumn, onDownloadXls, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="flex gap-4 justify-end">
      <q-btn color="blue" label="Export" icon-right="download" class="export-btn" @click="onDownloadXls" />
      <q-btn
        v-if="checkPermissions('ChequeIssueCreate')"
        color="green"
        to="/cheque-issue/add/"
        label="New Cheque Issue"
        class="add-btn"
        icon-right="add"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
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
                      :fetch-on-mount="true"
                      endpoint="v1/bank-account/choices/"
                      label="Bank Account"
                    />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Cleared']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-issued_to="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('ChequeIssueModify')"
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
            :to="`/cheque-issue/${props.row.id}/`"
          >
            {{ props.row.issued_to || props.row.party_name
            }}
          </router-link>
          <span v-else>{{ props.row.issued_to || props.row.party_name }}</span>
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="props.row.status == 'Issued'
                ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Cleared'
                  ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('ChequeIssueModify')"
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            style="font-size: 12px"
            :to="`/cheque-issue/${props.row.id}/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
