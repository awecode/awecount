<script>
import checkPermissions from '@/composables/checkPermissions'
import useList from '@/composables/useList'

export default defineNuxtComponent({
  setup() {
    const metaData = {
      title: 'Brands | Awecount',
    }
    const route = useRoute()
    useHead(metaData)
    const endpoint = `/api/company/${route.params.company}/brands/`
    return { ...useList(endpoint), checkPermissions }
  },
})
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        v-if="checkPermissions('brand.create')"
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New brand"
        :to="`/${$route.params.company}/inventory/brands/create`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="columns"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('brand.update')"
            class="text-blue"
            style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/inventory/brands/${props.row.id}/edit`"
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
