<template>
    <div class="row justify-end items-center" v-if="fields.transactions?.pagination.pages > 0">
        <div class="q-mr-sm">
            <span>
                {{ (fields.transactions?.pagination.page - 1) * 20 + 1 }} -
                {{
                    fields.transactions?.pagination.page ===
                    fields.transactions?.pagination.pages
                    ? fields.transactions?.pagination.count
                    : (fields.transactions?.pagination.page - 1) * 20 +
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
const props = defineProps({
    fields: {
        type: Object,
        required: true
    }
})
const goToPage = (pageNo) => {
    let newQuery = Object.assign({ ...route.query }, { page: pageNo })
    router.push(withQuery(`/account/${route.params.id}/view/`, newQuery))
}
</script>