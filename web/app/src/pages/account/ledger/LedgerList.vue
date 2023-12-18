<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('AccountCreate')" color="green" to="/account/add/" label="New Account" class="add-btn"
        icon-right="add" />
    </div>

    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.default" label="Is Default?" :false-value="null"></q-checkbox>
                  </div>
                  <div>
                    <q-checkbox v-model="filters.has_balance" label="Has Balance?" :false-value="null"></q-checkbox>
                  </div>
                  <div class="q-mx-sm">
                    <SelectWithFetch v-model.number="filters.category" endpoint="v1/categories/choices/"
                      label="Category" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="blue" dense flat to="" /> -->
          <q-btn v-if="checkPermissions('AccountView')" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            style="font-size: 12px" label="View" :to="`/account/${props.row.id}/view/`" />
          <q-btn v-if="checkPermissions('AccountModify')" label="Edit" color="orange-6"
            class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" :to="`/account/${props.row.id}/edit/`" />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('CategoryModify')" style="font-weight: 500; text-decoration: none"
            class="text-blue" :to="`/account-category/${props.row.category.id}/`">{{ props.row.category.name
            }}</router-link>
          <span v-else>{{ props.row.category.name }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-dr="props">
        <q-td :props="props">
          {{ parseInt(props.row.dr || 0) }}
        </q-td>
      </template>
      <template v-slot:body-cell-cr="props">
        <q-td :props="props">
          {{ parseInt(props.row.cr || 0) }}
        </q-td>
      </template>
      <template v-slot:body-cell-balance="props">
        <q-td :props="props">
          {{ parseInt(props.row.computed_balance || 0) }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const endpoint = '/v1/accounts/'
    const metaData = {
      title: 'Accounts | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const newColumn = [
      {
        name: 'code',
        label: 'Code',
        align: 'left',
        field: 'code',
        sortable: true
      },
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true
      },
      {
        name: 'category',
        label: 'Category',
        align: 'left',
        field: 'category',
        sortable: true
      },
      {
        name: 'dr',
        label: 'Dr',
        align: 'left',
        field: 'dr',
        sortable: true
      },
      {
        name: 'cr',
        label: 'Cr',
        align: 'left',
        field: 'cr',
        sortable: true
      },
      {
        name: 'computed_balance',
        label: 'Balance',
        align: 'left',
        field: 'computed_balance',
        sortable: true
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    const listData = useList(endpoint)
    watch(() => route.query, () => {
      if (route.path === '/account/') {
        // console.log(filters)

        let cleanedFilterValues = Object.fromEntries(
          Object.entries(route.query).map(([k, v]) => {
            if (v === 'true') {
              return [k, true]
            } else if (v === 'false') {
              return [k, false]
            } else if (k === 'search' && typeof v === 'string') {
              // TODO: added as an temproary solution need to confirm with dipesh sir
              return [k, isNaN(v) ? v : parseFloat(v)]
            }
            return [k, isNaN(v) ? v : parseFloat(v)]
          })
        )
        listData.filters.value = cleanedFilterValues
      }
    }, {
      deep: true
    })
    return { ...listData, newColumn, checkPermissions }
  },
}
</script>
