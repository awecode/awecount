<template>
  <div class="q-pa-md">
    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <span v-if="props.row.item__category__name">{{ props.row.item__category__name }}</span>
          <span v-else> Uncategorized Items </span>
        </q-td>
      </template>
      <template v-slot:bottom-row>
        <q-td class="font-medium">
          Total
        </q-td>
        <q-td class="font-medium">
          {{rows.reduce((accumulator, currentDict) => (accumulator + currentDict.quantity), 0)}}
        </q-td>
        <q-td class="font-medium">
          {{$nf(rows.reduce((accumulator, currentDict) => (accumulator + currentDict.tax_amount), 0))}}
        </q-td>
        <q-td class="font-medium">
          {{$nf(rows.reduce((accumulator, currentDict) => (accumulator + currentDict.discount_amount), 0))}}
        </q-td>
        <q-td class="font-medium">
          {{$nf(rows.reduce((accumulator, currentDict) => (accumulator + currentDict.net_amount), 0))}}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script lang="ts">
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
export default {
  setup() {
    const store = useLoginStore()
    const rows = ref([])
    const metaData = {
      title: 'Sales By Category | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'category',
        label: 'Category',
        align: 'left',
        field: 'item__category__name',
        sortable: true
      },
      {
        name: 'Total Quantity',
        label: 'Total Quantity',
        align: 'left',
        field: 'quantity',
        sortable: true
      },
      {
        name: 'tax_amount',
        label: 'Total Tax',
        align: 'left',
        field: (row: Record<string, number>) => $nf(row.tax_amount),
        sortable: true
      },
      {
        name: 'discount_amount',
        label: 'Total Discount',
        align: 'left',
        field: (row: Record<string, number>) => $nf(row.discount_amount),
        sortable: true
      },
      {
        name: 'net_amount',
        label: 'Net Amount',
        align: 'left',
        field: (row: Record<string, number>) => $nf(row.net_amount),
        sortable: true
      }
    ]

    return {
      rows,
      newColumn,
      checkPermissions,
      store,
      DateConverter,
    }
  },
  created() {
    const endpoint = 'v1/sales-row/by-category/'
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        if (data.length > 2) {
          this.rows = data.sort((a: Record<string, number>, b: Record<string, number>) => b.item__category - a.item__category);
        } else this.rows = data
      })
      .catch((error) => console.log(error))
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
