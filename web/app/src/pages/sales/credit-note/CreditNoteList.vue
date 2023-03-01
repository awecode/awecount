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
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <!-- <q-btn icon="visibility" color="blue" dense flat :to="`/journal-voucher/${props.row.id}/view/`" /> -->
          <q-btn
            color="blue"
            class="q-mr-md"
            label="View"
            :to="`/credit-note/${props.row.id}/view`"
          />
          <!-- <q-btn
            icon="delete"
            color="red"
            dense
            flat
            @click="confirmDeletion(props.row.id)"
          /> -->
          <!-- {{ props }} -->
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div
            class="text-white row items-center justify-center text-subtitle1 q-py-xs"
            :class="
              props.row.status == 'Issued'
                ? 'bg-blue'
                : props.row.status == 'Cleared'
                ? 'bg-green'
                : 'bg-red'
            "
            style="width: 80px; border-radius: 30px"
          >
            {{ props.row.status }}
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
