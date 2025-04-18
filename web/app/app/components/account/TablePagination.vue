<script setup>
import { withQuery } from 'ufo'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  fields: {
    type: Object,
    required: true,
  },
})
const router = useRouter()
const route = useRoute()
const pageSize = ref(route.query.page_size || 20)
const goToPage = (pageNo) => {
  const newQuery = Object.assign({ ...route.query }, { page: pageNo })
  router.push(withQuery(route.path, newQuery))
}
const updatePageSize = () => {
  const newQuery = Object.assign({ ...route.query }, { page_size: pageSize.value }, { page: undefined })
  router.push(withQuery(route.path, newQuery))
}
</script>

<template>
  <div v-if="fields.transactions?.pagination.pages > 0" class="row justify-end items-center">
    <span class="q-mr-md row items-center gap-4">
      <span>Records Per Page</span>
      <q-select
        v-model="pageSize"
        borderless
        dense
        small
        :options="[20, 30, 40, 50, 100, 200, 300, 400, 500]"
        @update:model-value="updatePageSize"
      />
    </span>
    <div class="q-mr-sm">
      <span>
        {{ (fields.transactions?.pagination.page - 1) * pageSize + 1 }} -
        {{ fields.transactions?.pagination.page === fields.transactions?.pagination.pages ? fields.transactions?.pagination.count : (fields.transactions?.pagination.page - 1) * pageSize + fields.transactions?.pagination.size }}
      </span>
      <span>&nbsp; of &nbsp;{{ fields.transactions?.pagination.count }}</span>
    </div>
    <q-btn
      dense
      flat
      round
      icon="first_page"
      :disable="fields.transactions?.pagination.page === 1"
      @click="() => goToPage(1)"
    />
    <q-btn
      dense
      flat
      round
      icon="chevron_left"
      :disable="fields.transactions?.pagination.page === 1"
      @click="() => goToPage(fields.transactions?.pagination.page - 1)"
    />
    <q-btn
      dense
      flat
      round
      icon="chevron_right"
      :disable="fields.transactions?.pagination.page === fields.transactions?.pagination.pages"
      @click="() => goToPage(fields.transactions?.pagination.page + 1)"
    />
    <q-btn
      dense
      flat
      round
      icon="last_page"
      :disable="fields.transactions?.pagination.page === fields.transactions?.pagination.pages"
      @click="() => goToPage(fields.transactions?.pagination.pages)"
    />
  </div>
</template>
