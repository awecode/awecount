<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const metaData = {
      title: 'Brands | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/brands/`
    return { ...useList(endpoint), checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        v-if="checkPermissions('BrandCreate')"
        color="green"
        :to="`/${$route.params.company}/brand/create/`"
        label="New brand"
        class="q-ml-lg add-btn"
        icon-right="add"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="columns"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('BrandModify')"
            class="text-blue"
            style="text-decoration: none"
            :to="`/${$route.params.company}/brand/${props.row.id}/`"
          >
            {{ props.row.name
            }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
