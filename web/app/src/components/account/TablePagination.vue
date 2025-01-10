<template>
    <div class="row justify-end items-center" v-if="fields.transactions?.pagination.pages > 0">
        <span class="q-mr-md row items-center gap-4">
            <span>Records Per Page</span>
            <q-select small borderless dense v-model="pageSize" @update:model-value="updatePageSize"
                :options="[20, 30, 40, 50, 100, 200, 300, 400, 500]">
            </q-select>
        </span>
        <div class="q-mr-sm">
            <span>
                {{ (fields.transactions?.pagination.page - 1) * pageSize + 1 }} -
                {{
                    fields.transactions?.pagination.page ===
                    fields.transactions?.pagination.pages
                    ? fields.transactions?.pagination.count
                    : (fields.transactions?.pagination.page - 1) * pageSize +
                    fields.transactions?.pagination.size
                }}
            </span>
            <span>&nbsp; of &nbsp;{{ fields.transactions?.pagination.count }}</span>
        </div>
        <q-btn icon="first_page" dense flat round :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(1)"></q-btn>
        <q-btn icon="chevron_left" dense flat round :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(fields.transactions?.pagination.page - 1)"></q-btn>
        <q-btn icon="chevron_right" dense flat round :disable="fields.transactions?.pagination.page ===
            fields.transactions?.pagination.pages
            " @click="() => goToPage(fields.transactions?.pagination.page + 1)"></q-btn>
        <q-btn icon="last_page" dense flat round :disable="fields.transactions?.pagination.page ===
            fields.transactions?.pagination.pages
            " @click="() => goToPage(fields.transactions?.pagination.pages)"></q-btn>
    </div>
</template>
<script setup>
import { withQuery } from 'ufo'
const router = useRouter()
const route = useRoute()
const pageSize = ref(route.query.page_size || 20)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
    fields: {
        type: Object,
        required: true
    }
})
const goToPage = (pageNo) => {
    let newQuery = Object.assign({ ...route.query }, { page: pageNo })
    router.push(withQuery(route.path, newQuery))
}
const updatePageSize = () => {
    let newQuery = Object.assign({ ...route.query }, { page_size: pageSize.value }, { page: undefined })
    router.push(withQuery(route.path, newQuery))
}
</script>
