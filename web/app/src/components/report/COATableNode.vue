<template>
  <tr
    class="hover:bg-gray-50"
    :class="{
      'bg-gray-100': draggingItem && row.id === currentTarget,
    }"
    draggable="true"
    @dragstart="handleDragStart({ type: 'category', row })"
    @dragover.prevent
    @dragend="handleDragEnd"
    @drop="
      handleDrop(
        row.id
          ? {
              type: 'category',
              row,
            }
          : null
      )
    "
    @dragenter="handleDragEnter({ type: 'category', row })"
    @dragleave="handleDragLeave"
  >
    <td
      class="flex items-center"
      :style="`padding-left: ${15 + 30 * (row.level || 0)}px;`"
    >
      <RouterLink
        style="text-decoration: none"
        target="_blank"
        :to="`/account/?has_balance=true&category=${row.id}`"
        class="text-blue-6"
        :class="props.root ? 'text-weight-bold' : ''"
        >{{ row.name }}</RouterLink
      >
      <q-btn
        dense
        flat
        round
        class="expand-btn"
        :class="expandedRows[row.id] ? 'expanded' : ''"
        @click="$emit('toggle-expand', row.id)"
        v-if="row.isExpandable"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="32"
          height="32"
          viewBox="0 0 24 24"
          class="text-grey-7"
        >
          <path
            fill="currentColor"
            d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z"
          />
        </svg>
      </q-btn>
    </td>
    <td></td>
    <td></td>
    <td></td>
    <td>{{ row.code }}</td>
    <td>{{ row.system_code }}</td>
    <td>{{ row.total_transactions }}</td>
  </tr>
  <template v-if="expandedRows[row.id]">
    <COATableNode
      v-for="child in row.children"
      :key="child.id"
      :row="child"
      :expandedRows="expandedRows"
      @toggle-expand="emitToggleExpand"
      @drag-event="$emit('drag-event', $event)"
      v-model="currentTarget"
      v-model:draggingItem="draggingItem"
    />
    <tr
      v-for="account in row.accounts"
      :key="account.id"
      draggable="true"
      :class="{
        'bg-gray-100': draggingItem && account.id === currentTarget,
      }"
      @dragstart="handleDragStart({ type: 'account', row: account })"
      @dragover.prevent
      @dragend="handleDragEnd"
      @drop="
        handleDrop({
          type: 'account',
          row: account,
        })
      "
      @dragenter="handleDragEnter({ type: 'account', row: account })"
      @dragleave="handleDragLeave"
    >
      <td :style="`padding-left: ${15 + 30 * ((row.level || 0) + 1)}px`">
        <RouterLink
          target="_blank"
          style="text-decoration: none"
          :to="`/account/${account.id}/view/`"
          class="text-blue-7 text-italic text-weight-regular"
          >{{ account.name }}</RouterLink
        >
      </td>
      <td></td>
      <td></td>
      <td></td>
      <td>{{ account.id }}</td>
      <td>{{ account.system_code }}</td>
      <td>{{ account.total_transactions }}</td>
    </tr>
  </template>
</template>

<script setup lang="ts">
import { PropType, ref } from 'vue'

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

const emit = defineEmits([
  'toggle-expand',
  'drag-event',
  'clear-current-target',
])

function emitToggleExpand(id: number, action: 'open' | 'close' | undefined) {
  emit('toggle-expand', id, action)
}

const props = defineProps({
  row: {
    type: Object as PropType<CategoryTree>,
    required: true,
  },
  expandedRows: {
    type: Object as PropType<Record<number, boolean>>,
    required: true,
  },
  root: {
    type: Boolean,
    default: false,
  },
})

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

const currentTarget = defineModel<number | null>()

const toggleExpandTimeout = ref<NodeJS.Timeout | null>(null)

function startToggleExpandTimeout(id: number) {
  stopToggleExpandTimeout()
  toggleExpandTimeout.value = setTimeout(() => {
    emit('toggle-expand', id, 'open')
  }, 1000)
}

function stopToggleExpandTimeout() {
  if (toggleExpandTimeout.value) {
    clearTimeout(toggleExpandTimeout.value)
  }
}

const handleDragStart = (item: DragItem) => {
  draggingItem.value = item
}

const handleDragEnter = (item: DragItem) => {
  currentTarget.value = null
  if (item.type === 'category') {
    startToggleExpandTimeout(item.row.id)
  }
  currentTarget.value = item.row.id
}

const handleDragLeave = () => {
  stopToggleExpandTimeout()
}

const handleDragEnd = () => {
  draggingItem.value = null
  currentTarget.value = null
}

const handleDrop = (target: DragItem | null) => {
  stopToggleExpandTimeout()
  if (!draggingItem.value) return

  if (
    draggingItem.value.type === 'category' &&
    target &&
    target.type === 'category'
  ) {
    if (
      target.row.tree_id === draggingItem.value.row.tree_id &&
      target.row.level > draggingItem.value.row.level
    )
      return
    else if (target.row.id === draggingItem.value.row.parent_id) return
  }

  if (draggingItem.value.type === 'account' && !target) return

  if (
    draggingItem.value.type === 'account' &&
    target &&
    target.type === 'account'
  ) {
    if (target.row.category_id === draggingItem.value.row.category_id) return
  }

  if (draggingItem.value.type === 'account' && target!.type === 'category') {
    if (target!.row.id === draggingItem.value.row.category_id) return
  }

  const sourceId =
    draggingItem.value.type === 'category'
      ? draggingItem.value.row.id
      : draggingItem.value.row.category_id
  const targetId = target
    ? target.type === 'account'
      ? target.row.category_id
      : target.row.id
    : null

  if (sourceId === targetId) return

  emit('drag-event', {
    source: {
      type: draggingItem.value.type,
      id: draggingItem.value.row.id,
    },
    target: targetId,
  })

  draggingItem.value = null
}
</script>
