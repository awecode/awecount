<template>
    <div class="mt-4">
        <div v-if="pagination.pages > 1" id="v-pagination-container">
            <nav>
                <ul class="d-print-none btns-con items-end">
                    <li class="page-item">
                        <q-btn v-if="pagination.previous" @click="changePage(pagination.page - 1)"
                            icon="mdi-chevron-left" class="q-px-sm"></q-btn>
                    </li>
                    <li v-for="pg in page_links" :key="pg" class="page-item">
                        <q-btn v-if="Number.isInteger(pg)" @click="changePage(pg)" :class="{
                            'v-pagination__item--active primary': pg == pagination.page
                        }">{{ pg }}</q-btn>
                        <span v-else class="v-pagination__item disabled">{{ pg }}</span>
                    </li>

                    <li v-if="pagination.next" class="page-item">
                        <q-btn :disable="!pagination.next" @click="changePage(pagination.page + 1)" icon="mdi-chevron-right"
                            class="q-px-sm"></q-btn>
                    </li>
                </ul>
            </nav>
        </div>
        <div class="pl-2 text-center">{{ pagination.count }} result{{
            pagination.count === 1 ? "" : "s"
        }}</div>
    </div>
</template>
  
<script setup>
const props = defineProps(["pagination", "endpoint", "collectionName", "get"])
const emit = defineEmits(['updatePage'])
const route = useRoute()
const router = useRouter()
const page_links = computed(() => {
    let c = props.pagination.page;
    let m = props.pagination.pages;
    let delta = 2;
    let range = [];
    let rangeWithDots = [];
    let l;
    range.push(1);
    for (let i = c - delta; i <= c + delta; i++) {
        if (i < m && i > 1) {
            range.push(i);
        }
    }
    range.push(m);
    for (let i of range) {
        if (l) {
            if (i - l === 2) {
                rangeWithDots.push(l + 1);
            } else if (i - l !== 1) {
                rangeWithDots.push("...");
            }
        }
        rangeWithDots.push(i);
        l = i;
    }

    return rangeWithDots;
})
// const fetchPage = (page) => {
//     // this.get(this.endpoint, page, this.collection_name);
// }
// const getLink = (pg) => {
//     return { path: route.fullPath, query: { page: pg } };
// }
const changePage = (page) => {
    // router.push({
    //     path: $route.fullPath,
    //     query: { search: route.query.search, page: page }
    // })
    emit('updatePage', page)
} 
</script>
<!-- <script>
export default {
    props: ,

};
</script> -->
<style scoped>
li {
    list-style: none;
}

.v-pagination__item--active.primary {
    background-color: lightgray;
}

.btns-con {
    display: flex;
    gap: 10px;
}

a {
    color: rgb(55, 55, 55);
}
</style>