<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        color="blue"
        to="/credit-note/add/"
        label="Exoprt Xls"
        icon-right="download"
      />
      <q-btn
        color="green"
        to="/credit-note/add/"
        label="New Credit Note"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      title="Accounts"
      :rows="rows"
      :columns="columns"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-input
          borderless
          dense
          debounce="500"
          v-model="searchQuery"
          placeholder="Search"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props" class="row justify center">
          <q-btn
            color="blue"
            class="q-mr-md"
            label="View"
            :to="`/credit-note/${props.row.id}/view`"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
            <div
              class="text-white text-subtitle2 row items-center justify-center"
              :class="
                props.row.status == 'Issued'
                  ? 'bg-blue'
                  : props.row.status == 'Resolved'
                  ? 'bg-green'
                  : 'bg-red'
              "
              style="border-radius: 30px; padding: 5px 15px"
            >
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
export default {
  setup() {
    const endpoint = '/v1/credit-note/'
    return { ...useList(endpoint) }
  },
}
</script>
