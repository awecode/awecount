<script setup>
const props = defineProps(['pagination', 'endpoint', 'collectionName', 'get'])
const emit = defineEmits(['updatePage'])
const page_links = computed(() => {
  const c = props.pagination.page
  const m = props.pagination.pages
  const delta = 2
  const range = []
  const rangeWithDots = []
  let l
  range.push(1)
  for (let i = c - delta; i <= c + delta; i++) {
    if (i < m && i > 1) {
      range.push(i)
    }
  }
  range.push(m)
  for (const i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1)
      } else if (i - l !== 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = i
  }

  return rangeWithDots
})
const changePage = (page) => {
  emit('updatePage', page)
}
</script>

<template>
  <div class="mt-4">
    <div v-if="pagination.pages > 1" id="v-pagination-container">
      <nav>
        <ul class="d-print-none btns-con items-end">
          <li class="page-item">
            <q-btn
              v-if="pagination.previous"
              class="q-px-sm"
              icon="mdi-chevron-left"
              @click="changePage(pagination.page - 1)"
            />
          </li>
          <li v-for="pg in page_links" :key="pg" class="page-item">
            <q-btn
              v-if="Number.isInteger(pg)"
              :class="{
                'v-pagination__item--active primary': pg == pagination.page,
              }"
              @click="changePage(pg)"
            >
              {{ pg }}
            </q-btn>
            <span v-else class="v-pagination__item disabled">{{ pg }}</span>
          </li>

          <li v-if="pagination.next" class="page-item">
            <q-btn
              class="q-px-sm"
              icon="mdi-chevron-right"
              :disable="!pagination.next"
              @click="changePage(pagination.page + 1)"
            />
          </li>
        </ul>
      </nav>
    </div>
    <div class="pl-2 text-center">
      {{ pagination.count }} result{{ pagination.count === 1 ? '' : 's' }}
    </div>
  </div>
</template>

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
