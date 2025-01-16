<script setup>
import { $api } from 'src/composables/api'

const data = ref({})
useMeta(() => {
  return {
    title: `${data.value.name || 'Item'}| Awecount`,
  }
})
const route = useRoute()
data.value = await $api(`/api/company/${route.params.company}/items/${route.params.id}/details/`, {
  method: 'GET',
})
</script>

<template>
  <q-card class="q-ma-lg q-pa-lg">
    <div v-if="data.front_image?.length > 0 || data.back_image?.length > 0" class="row q-gutter-x-lg pb-8">
      <div v-if="data.front_image?.length > 0" class="col-4">
        <a class="q-full-width" target="_blank" :href="data.front_image">
          <img :src="data.front_image" />
        </a>
      </div>
      <div v-if="data.back_image?.length > 0" class="col-4">
        <a class="q-full-width" target="_blank" :href="data.back_image">
          <img class="q-full-width" :src="data.back_image" />
        </a>
      </div>
    </div>
    <div>
      <div>
        <div class="flex pb-2">
          <div class="text-h5">
            <span class="text-bold">{{ data?.name || '-' }}</span>
            <span v-if="data?.code" class="ml-4 text-h6 text-grey-9 text-sm p-2 inline-block">[Code: {{ data.code }}]</span>
          </div>
        </div>

        <div class="mb-4">
          <div class="q-mb-xs">
            <span class="h6 text-weight-bold q-mr-sm">Cost Price:</span>
            <span>Nrs. {{ data.cost_price }}</span>
          </div>
          <div class="q-mb-xs">
            <span class="h6 text-weight-bold q-mr-sm">Selling Price:</span>
            <span>Nrs. {{ data.selling_price }}</span>
          </div>
          <div v-if="data.brand?.id" class="q-mb-xs">
            <span class="h6 text-weight-bold q-mr-sm">Brand:</span>
            <router-link :to="`/${$route.params.company}/brand/${data.brand?.id}`">
              <span class="link">
                {{ data.brand?.name }}
              </span>
            </router-link>
          </div>
          <div v-if="data.description" class="q-my-lg">
            {{ data.description }}
          </div>
        </div>
        <div>
          <q-chip v-if="data.can_be_sold">
            Can be Sold
          </q-chip>
          <q-chip v-if="data.can_be_purchased">
            Can be Purchased
          </q-chip>
          <q-chip v-if="data.track_inventory">
            Inventory is Tracked
          </q-chip>
          <q-chip v-if="data.fixed_asset">
            Is a Fixed Asset
          </q-chip>
          <q-chip v-if="data.direct_expense">
            Is a Direct Expense
          </q-chip>
          <q-chip v-if="data.indirect_expense">
            Is an Indirect Expense
          </q-chip>
        </div>
      </div>
    </div>
    <q-table
      hide-bottom
      class="q-my-lg"
      title="Accounts"
      :columns="[
        { name: 'ac', field: 'ac', label: 'Account', align: 'left' },
        { name: 'dr', field: 'dr', label: 'DR.', align: 'left' },
        { name: 'cr', field: 'cr', label: 'CR.', align: 'left' },
        { name: 'bal', field: 'bal', label: 'Balance', align: 'left' },
      ]"
      :rows="[
        {
          ac: 'asvahsv',
          dr: 120,
          cr: 150,
          bal: 30,
        },
      ]"
    >
      <!-- :rows="[
        {
          ac: 'asvahsv',
          dr: 120,
          cr: 150,
          bal: 30,
        },
        {
          ac: 'Sales',
          dr: data.sales_account?.amounts.dr,
          cr: data.sales_account?.amounts.cr,
          bal:
            (data.sales_account?.amounts.dr || 0) -
            (data.sales_account?.amounts.cr || 0),
        },
      ]" -->
      <template #body="props">
        <q-tr v-if="data.account" :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/inventory/ledgers/${data.account?.id}`">
              Stock
            </router-link>
          </q-td>
          <q-td>{{ data.account?.amounts.dr }}</q-td>
          <q-td>{{ data.account?.amounts.cr }}</q-td>
          <q-td>
            {{ (data.account?.amounts.dr || 0) - (data.account?.amounts.cr || 0) }}
          </q-td>
        </q-tr>
        <q-tr :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/account/ledgers/${data.sales_account?.id}`">
              Sales
            </router-link>
          </q-td>
          <q-td>{{ data.sales_account?.amounts.dr }}</q-td>
          <q-td>{{ data.sales_account?.amounts.cr }}</q-td>
          <q-td>
            {{ (data.sales_account?.amounts.dr || 0) - (data.sales_account?.amounts.cr || 0) }}
          </q-td>
        </q-tr>
        <q-tr v-if="data.purchase_account" :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/account/ledgers/${data.purchase_account?.id}`">
              Purchase
            </router-link>
          </q-td>
          <q-td>{{ data.purchase_account?.amounts.dr }}</q-td>
          <q-td>{{ data.purchase_account?.amounts.cr }}</q-td>
          <q-td>
            {{ (data.purchase_account?.amounts.dr || 0) - (data.purchase_account?.amounts.cr || 0) }}
          </q-td>
        </q-tr>
        <q-tr v-if="data.expense_account" :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/account/ledgers/${data.expense_account?.id}`">
              Expenses
            </router-link>
          </q-td>
          <q-td>{{ data.expense_account?.amounts.dr }}</q-td>
          <q-td>{{ data.expense_account?.amounts.cr }}</q-td>
          <q-td>
            {{ (data.expense_account?.amounts.dr || 0) - (data.expense_account?.amounts.cr || 0) }}
          </q-td>
        </q-tr>
        <q-tr v-if="data.fixed_asset_account" :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/account/ledgers/${data.fixed_asset_account?.id}`">
              Fixed Assets
            </router-link>
          </q-td>
          <q-td>{{ data.fixed_asset_account?.amounts.dr }}</q-td>
          <q-td>{{ data.fixed_asset_account?.amounts.cr }}</q-td>
          <q-td>
            {{ (data.fixed_asset_account?.amounts.dr || 0) - (data.fixed_asset_account?.amounts.cr || 0) }}
          </q-td>
        </q-tr>
        <q-tr v-if="data.discount_received_account" :props="props">
          <q-td>
            <router-link :to="`/${$route.params.company}/account/ledgers/${data.discount_received_account?.id}`">
              Discount Received
            </router-link>
          </q-td>
          <q-td>{{ $nf(data.discount_received_account?.amounts.dr) }}</q-td>
          <q-td>{{ $nf(data.discount_received_account?.amounts.cr) }}</q-td>
          <q-td>
            {{ $nf((data.discount_received_account?.amounts.dr || 0) - (data.discount_received_account?.amounts.cr || 0)) }}
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <router-link class="no-underline" :to="`/${$route.params.company}/inventory/items/${data.id}`">
      <q-btn class="q-mt-md q-px-lg no-underline" color="orange-7">
        Edit
      </q-btn>
    </router-link>
  </q-card>
</template>

<style scoped>
img {
  width: 100%;
  object-fit: contain;
}

a {
  text-decoration: none;
  color: cornflowerblue;
}
</style>
