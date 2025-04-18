<script setup lang="ts">
import type { PropType } from 'vue'
import checkPermissions from '@/composables/checkPermissions'
import { useLoginStore } from '@/stores/login-info'
import { ref } from 'vue'

interface Account {
  id: number
  name: string
  code: string
  system_code: string | null
  category_id: number
  total_transactions: number
}

interface CategoryTree {
  id: number
  name: string
  children: CategoryTree[]
  code: string | null
  system_code: string | null
  total_transactions: number
  accounts: Account[]
  level: number
  tree_id: number
  isExpandable: boolean
  parent_id: number
}

const props = defineProps({
  row: {
    type: Object as PropType<CategoryTree>,
    required: true,
  },
  root: {
    type: Boolean,
    default: false,
  },
  droppableCategories: {
    type: Array as PropType<number[]>,
    required: false,
    default: () => [],
  },
  config: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['drag-event', 'edit-row', 'add-category', 'add-account'])

const canBeDropped = computed(() => props.droppableCategories.includes(props.row.id))

type DragItem =
  | {
    type: 'category'
    row: CategoryTree
  }
  | {
    type: 'account'
    row: Account
  }

const draggingItem = defineModel<DragItem | null>('draggingItem')

const currentTarget = defineModel<CategoryTree | null>('currentTarget')

const toggleExpandTimeout = ref<NodeJS.Timeout | null>(null)

function startToggleExpandTimeout(id: number) {
  toggleExpandTimeout.value = setTimeout(() => {
    if (!currentTarget.value || currentTarget.value.id !== id) {
      return
    }
    changeExpandStatus(id, 'open')
  }, 1000)
}
const handleDragStart = (item: DragItem) => {
  draggingItem.value = item
}

const stopToggleExpandTimeout = () => {
  if (toggleExpandTimeout.value) {
    clearTimeout(toggleExpandTimeout.value)
    toggleExpandTimeout.value = null
  }
}

const handleDragEnter = (item: CategoryTree) => {
  currentTarget.value = null
  stopToggleExpandTimeout()
  if (item.id !== draggingItem.value?.row.id) {
    startToggleExpandTimeout(item.id)
  }
  currentTarget.value = item
}

const handleDragEnd = () => {
  draggingItem.value = null
  currentTarget.value = null
}

const handleDrop = (target: DragItem | null) => {
  if (!canBeDropped.value) {
    draggingItem.value = null
    currentTarget.value = null
    return
  }

  emit('drag-event', {
    source: {
      type: draggingItem.value!.type,
      id: draggingItem.value!.row.id,
    },
    target:
      target
        ? target.type === 'account'
          ? target.row.category_id
          : target.row.id
        : null,
  })

  draggingItem.value = null
  currentTarget.value = null
}

const loginStore = useLoginStore()

const changeExpandStatus = (id: number, type: 'open' | 'close' | null = null) => {
  // @ts-expect-error loginStore is js store
  const index = loginStore.chartOfAccountsExpandId.indexOf(id)

  if (type === 'close') {
    if (index >= 0) loginStore.chartOfAccountsExpandId.splice(index, 1)
  } else if (type === 'open') {
    if (index < 0) {
      // @ts-expect-error loginStore is js store
      loginStore.chartOfAccountsExpandId.push(id)
    }
  } else {
    if (index >= 0) loginStore.chartOfAccountsExpandId.splice(index, 1)
    // @ts-expect-error loginStore is js store
    else loginStore.chartOfAccountsExpandId.push(id)
  }
}

const expandStatus = computed(() => {
  const newTotalObjStatus
    // @ts-expect-error loginStore is js store
    = props.row.id && loginStore.chartOfAccountsExpandId.includes(props.row.id)
  return newTotalObjStatus
})

const editRow = (type: 'category' | 'account', id: number) => {
  emit('edit-row', type, id)
}

function handleEditRowEmit(type: 'category' | 'account', id: number) {
  emit('edit-row', type, id)
}

const dropdown = ref(false)

const addSubCategory = (id: number) => {
  emit('add-category', id)
}

const addAccount = (id: number) => {
  emit('add-account', id)
}
</script>

<template>
  <q-tr
    v-if="!config.hide_categories"
    class="hover:bg-gray-50 q-virtual-scroll--skip"
    :class="{
      'bg-gray-100': canBeDropped,
      'bg-gray-200': currentTarget && currentTarget.id === row.id && canBeDropped,
    }"
    :draggable="checkPermissions('category.update') && row.id ? true : false"
    @dragend="handleDragEnd"
    @dragenter="handleDragEnter(row)"
    @dragover.prevent
    @dragstart="handleDragStart({ type: 'category', row })"
    @drop="
      handleDrop(
        row.id
          ? {
            type: 'category',
            row,
          }
          : null,
      )
    "
  >
    <q-td class="flex items-center" :style="`padding-left: ${15 + 30 * (row.level || 0)}px;`">
      <RouterLink
        class="text-blue-6"
        style="text-decoration: none"
        target="_blank"
        :class="props.root ? 'text-weight-bold' : ''"
        :to="`/account/ledgers/?has_balance=true&category=${row.id}`"
      >
        {{ row.name }}
      </RouterLink>
      <q-btn
        v-if="row.isExpandable"
        dense
        flat
        round
        class="expand-btn"
        :class="expandStatus ? 'expanded' : ''"
        @click="changeExpandStatus(row.id)"
      >
        <svg
          class="text-grey-7"
          height="32"
          viewBox="0 0 24 24"
          width="32"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" fill="currentColor" />
        </svg>
      </q-btn>
    </q-td>
    <q-td>{{ row.code }}</q-td>
    <q-td>{{ row.system_code }}</q-td>
    <q-td>{{ row.id !== 0 ? row.total_transactions : '' }}</q-td>
    <q-td class="text-center">
      <q-btn-dropdown
        v-if="row.id"
        v-model="dropdown"
        flat
        round
        class="text-blue-6"
        dropdown-icon="more_vert"
        size="sm"
      >
        <q-list>
          <q-item
            v-if="checkPermissions('category.update')"
            v-close-popup
            clickable
            @click="editRow('category', row.id)"
          >
            <q-item-section>Edit Category</q-item-section>
          </q-item>
          <q-item
            v-if="checkPermissions('category.create')"
            v-close-popup
            clickable
            @click="addSubCategory(row.id)"
          >
            <q-item-section>Add Sub-Category</q-item-section>
          </q-item>
          <q-item
            v-if="checkPermissions('account.create')"
            v-close-popup
            clickable
            @click="addAccount(row.id)"
          >
            <q-item-section>Add Account</q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </q-td>
  </q-tr>
  <template v-if="config.hide_categories || expandStatus">
    <template v-for="child in row.children" :key="`coa-child-${child.id}`">
      <COATableNode
        v-if="!(config.hide_zero_transactions && child.total_transactions === 0)"
        v-model:current-target="currentTarget"
        v-model:dragging-item="draggingItem"
        :config="config"
        :droppable-categories="droppableCategories"
        :row="child"
        @add-account="$emit('add-account', $event)"
        @add-category="$emit('add-category', $event)"
        @drag-event="$emit('drag-event', $event)"
        @edit-row="handleEditRowEmit"
      />
    </template>
    <template v-if="!config.hide_accounts">
      <template v-for="account in row.accounts" :key="account.id">
        <q-tr
          v-if="!(config.hide_zero_transactions && account.total_transactions === 0)"
          class="q-virtual-scroll--with-prev"
          :draggable="checkPermissions('account.update') && !config.hide_categories ? true : false"
          @dragover.prevent
          @dragstart="handleDragStart({ type: 'account', row: account })"
        >
          <q-td :style="`padding-left: ${15 + (!config.hide_categories ? 30 * ((row.level || 0) + 1) : 0)}px`">
            <RouterLink
              class="text-blue-7 text-italic text-weight-regular"
              style="text-decoration: none"
              target="_blank"
              :to="`/${$route.params.company}/account/ledgers/${account.id}`"
            >
              {{ account.name }}
            </RouterLink>
          </q-td>
          <q-td>{{ account.id }}</q-td>
          <q-td>{{ account.system_code }}</q-td>
          <q-td>{{ account.total_transactions }}</q-td>
          <q-td class="text-center">
            <q-btn
              v-if="checkPermissions('account.update')"
              dense
              flat
              round
              class="text-blue-6"
              icon="edit"
              size="sm"
              @click="editRow('account', account.id)"
            />
          </q-td>
        </q-tr>
      </template>
    </template>
  </template>
</template>
