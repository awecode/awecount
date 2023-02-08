<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn color="green" to="/bank/account/add/" label="New Account" class="q-ml-lg" icon-right="add" />
    </div>

    <q-table title="Accounts" :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md">
      <template v-slot:top-right>
        <q-input borderless dense debounce="500" v-model="searchQuery" placeholder="Search">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <!-- <q-btn icon="visibility" color="blue" label="Account" dense :to="`/account/${props.row.id}/view/`" /> -->
          <q-btn color="blue" class="q-mr-md" label="View" :to="`/account/${props.row.id}/view/`" />

          <q-btn icon="edit" color="amber" dense flat :to="`/bank/account/${props.row.id}/edit/`" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/bank-account/'
    const listData = useList(endpoint)

    return { ...listData }
  },
}
</script>
