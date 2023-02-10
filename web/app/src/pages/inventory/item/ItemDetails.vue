<template>
  <q-card class="q-ma-lg q-pa-lg">
    <div
      v-if="data.front_image?.length > 0 || data.back_image?.length > 0"
      class="row q-gutter-x-lg"
    >
      <div class="col-4" v-if="data.front_image?.length > 0">
        <a :href="data.front_image" target="_blank" class="q-full-width">
          <img :src="data.front_image" />
        </a>
      </div>
      <div class="col-4" v-if="data.back_image?.length > 0">
        <a :href="data.back_image" target="_blank" class="q-full-width">
          <img :src="data.back_image" class="q-full-width" />
        </a>
      </div>
    </div>
    <div>
      <h5 class="row q-gutter-x-lg">
        <span>{{ data.name }}</span
        ><span class="text-grey-7">{{ data.code }}</span>
      </h5>
      <div>
        <div class="q-mb-xs">
          <span class="h6 text-weight-bold q-mr-sm">Cost Price:</span
          ><span>Nrs. {{ data.cost_price }}</span>
        </div>
        <div class="q-mb-xs">
          <span class="h6 text-weight-bold q-mr-sm">Selling Price:</span
          ><span>Nrs. {{ data.selling_price }}</span>
        </div>
        <div class="q-mb-xs">
          <span class="h6 text-weight-bold q-mr-sm">Brand:</span>
          <router-link :to="`/brand/${data.brand?.id}`"
            ><span class="link">
              {{ data.brand?.name }}
            </span></router-link
          >
        </div>
        <div v-if="data.description" class="q-my-lg">
          {{ data.description }}
        </div>
        <div>
          <q-chip v-if="data.can_be_sold">Can be Sold</q-chip>
          <q-chip v-if="data.can_be_purchased">Can be Purchased</q-chip>
          <q-chip v-if="data.track_inventory">Inventory is Tracked</q-chip>
          <q-chip v-if="data.fixed_asset">Is a Fixed Asset</q-chip>
          <q-chip v-if="data.direct_expense">Is a Direct Expense</q-chip>
          <q-chip v-if="data.indirect_expense">Is an Indirect Expense</q-chip>
        </div>
      </div>
    </div>
    <q-table
      class="q-my-lg"
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
        {
          ac: 'Sales',
          dr: data.sales_account?.amounts.dr,
          cr: data.sales_account?.amounts.cr,
          bal:
            (data.sales_account?.amounts.dr || 0) -
            (data.sales_account?.amounts.cr || 0),
        },
      ]"
      :binary-state-sort="true"
      title="Accounts"
    >
    </q-table>
  </q-card>
</template>

<script setup>
const route = useRoute();
const data = ref({});
useGetDataAuth(`/v1/items/${route.params.id}/details/`, {
  method: 'GET',
}).then((res) => (data.value = res));
</script>

<style scoped>
img {
  width: 100%;
  object-fit: contain;
}
.link {
  text-decoration: none;
  color: cornflowerblue;
}
</style>
