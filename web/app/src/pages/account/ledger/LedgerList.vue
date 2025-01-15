<script>
export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/accounts/`
    const metaData = {
      title: 'Accounts | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'code',
        label: 'Code',
        align: 'left',
        field: 'code',
        sortable: true,
      },
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true,
      },
      {
        name: 'category',
        label: 'Category',
        align: 'left',
        field: 'category',
        sortable: true,
      },
      // {
      //   name: 'dr',
      //   label: 'Dr',
      //   align: 'left',
      //   field: 'dr',
      //   sortable: true
      // },
      // {
      //   name: 'cr',
      //   label: 'Cr',
      //   align: 'left',
      //   field: 'cr',
      //   sortable: true
      // },
      // {
      //   name: 'computed_balance',
      //   label: 'Balance',
      //   align: 'left',
      //   field: 'computed_balance',
      //   sortable: true
      // },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    const listData = useList(endpoint)
    watch(
      () => route.query,
      () => {
        if (route.path === '/account/') {
          const queryParams = { ...route.query }
          if (queryParams.hasOwnProperty('search') && typeof queryParams.search === 'string') {
            listData.searchQuery.value = queryParams.search
          } else {
            listData.searchQuery.value = null
          }
          delete queryParams.search
          const cleanedFilterValues = Object.fromEntries(
            Object.entries(queryParams).map(([k, v]) => {
              if (v === 'true') {
                return [k, true]
              } else if (v === 'false') {
                return [k, false]
              }
              return [k, Number.isNaN(v) ? v : Number.parseFloat(v)]
            }),
          )
          listData.filters.value = cleanedFilterValues
        }
      },
      {
        deep: true,
      },
    )
    return { ...listData, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('account.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Account"
        :to="`/${$route.params.company}/account/create/`"
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
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.default" label="Is Default?" :false-value="null" />
                  </div>
                  <div>
                    <q-checkbox v-model="filters.has_balance" label="Has Balance?" :false-value="null" />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2
                      v-model="filters.category"
                      label="Category"
                      :endpoint="`/api/company/${$route.params.company}/categories/choices/`"
                      :fetch-on-mount="true"
                    />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
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
      <template #body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="blue" dense flat to="" /> -->
          <q-btn
            v-if="checkPermissions('account.view')"
            class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            color="blue"
            label="View"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account/${props.row.id}/view/`"
          />
          <q-btn
            v-if="checkPermissions('account.modify')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-6"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account/${props.row.id}/edit/`"
          />
        </q-td>
      </template>
      <template #body-cell-category="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('category.modify')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/account-category/${props.row.category.id}/`"
          >
            {{ props.row.category.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.category.name }}
          </span>
        </q-td>
      </template>
      <template #body-cell-dr="props">
        <q-td :props="props">
          {{ parseInt(props.row.dr || 0) }}
        </q-td>
      </template>
      <template #body-cell-cr="props">
        <q-td :props="props">
          {{ parseInt(props.row.cr || 0) }}
        </q-td>
      </template>
      <template #body-cell-balance="props">
        <q-td :props="props">
          {{ parseInt(props.row.computed_balance || 0) }}
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('account.view')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/account/${props.row.id}/view/`"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
