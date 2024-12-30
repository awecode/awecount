<template>
  <tr
    v-if="!config.hide_categories"
    class="hover:bg-gray-50"
    :class="{
      'bg-gray-100':
        draggingItem &&
        currentTarget &&
        row.id === currentTarget.row.id &&
        currentTarget.type === 'category' &&
        canBeDropped,
    }"
    :draggable="checkPermissions('CategoryModify') && row.id ? true : false"
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
        >{{ row.name }}
      </RouterLink>
      <q-btn
        dense
        flat
        round
        class="expand-btn"
        :class="expandStatus ? 'expanded' : ''"
        @click="changeExpandStatus(row.id)"
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
    <td>{{ row.id !== 0 ? row.total_transactions : '' }}</td>
    <td class="text-center">
      <q-btn-dropdown
        v-if="row.id"
        v-model="dropdown"
        class="text-blue-6"
        size="sm"
        flat
        round
        dropdown-icon="more_vert"
      >
        <q-list>
          <q-item
            v-if="checkPermissions('CategoryModify')"
            clickable
            v-close-popup
            @click="editRow('category', row.id)"
          >
            <q-item-section>Edit Category</q-item-section>
          </q-item>
          <q-item
            v-if="checkPermissions('CategoryCreate')"
            clickable
            v-close-popup
            @click="addSubCategory(row.id)"
          >
            <q-item-section>Add Sub-Category</q-item-section>
          </q-item>
          <q-item
            v-if="checkPermissions('AccountCreate')"
            clickable
            v-close-popup
            @click="addAccount(row.id)"
          >
            <q-item-section>Add Account</q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </td>
  </tr>
  <template v-if="expandStatus">
    <template v-for="child in row.children" :key="`coa-child-${child.id}`">
      <COATableNode
        v-if="
          !(config.hide_zero_transactions && child.total_transactions === 0)
        "
        :row="child"
        @drag-event="$emit('drag-event', $event)"
        @add-category="$emit('add-category', $event)"
        @add-account="$emit('add-account', $event)"
        v-model:current-target="currentTarget"
        v-model:draggingItem="draggingItem"
        :canBeDropped="canBeDropped"
        @edit-row="handleEditRowEmit"
        :config="config"
      />
    </template>
    <template v-if="!config.hide_accounts">
      <template v-for="account in row.accounts" :key="account.id">
        <tr
          v-if="
            !(config.hide_zero_transactions && account.total_transactions === 0)
          "
          :draggable="checkPermissions('AccountModify') ? true : false"
          :class="{
            'bg-gray-100':
              draggingItem &&
              currentTarget &&
              account.id === currentTarget.row.id &&
              currentTarget.type === 'account' &&
              canBeDropped,
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
        >
          <td
            :style="`padding-left: ${
              15 + (!config.hide_categories ? 30 * ((row.level || 0) + 1) : 0)
            }px`"
          >
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
          <td class="text-center">
            <q-btn
              v-if="checkPermissions('AccountModify')"
              dense
              flat
              round
              icon="edit"
              size="sm"
              class="text-blue-6"
              @click="editRow('account', account.id)"
            />
          </td>
        </tr>
      </template>
    </template>
  </template>
</template>

<script setup lang="ts">
import checkPermissions from 'src/composables/checkPermissions'
import { useLoginStore } from 'src/stores/login-info'
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
  'drag-event',
  'edit-row',
  'add-category',
  'add-account',
])

const props = defineProps({
  row: {
    type: Object as PropType<CategoryTree>,
    required: true,
  },
  root: {
    type: Boolean,
    default: false,
  },
  canBeDropped: {
    type: Boolean,
    required: true,
  },
  config: {
    type: Object,
    required: true,
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

const currentTarget = defineModel<DragItem | null>('currentTarget')

const toggleExpandTimeout = ref<NodeJS.Timeout | null>(null)

function startToggleExpandTimeout(id: number) {
  toggleExpandTimeout.value = setTimeout(() => {
    if (
      !currentTarget.value ||
      currentTarget.value.type !== 'category' ||
      currentTarget.value.row.id !== id
    ) {
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

const handleDragEnter = (item: DragItem) => {
  currentTarget.value = null
  stopToggleExpandTimeout()
  if (item.type === 'category' && item.row.id !== draggingItem.value?.row.id) {
    startToggleExpandTimeout(item.row.id)
  }
  currentTarget.value = item
}

const handleDragEnd = () => {
  draggingItem.value = null
  currentTarget.value = null
}

const handleDrop = (target: DragItem | null) => {
  if (!props.canBeDropped) {
    draggingItem.value = null
    currentTarget.value = null
    return
  }

  emit('drag-event', {
    source: {
      type: draggingItem.value!.type,
      id: draggingItem.value!.row.id,
    },
    target: target
      ? target.type === 'account'
        ? target.row.category_id
        : target.row.id
      : null,
  })

  draggingItem.value = null
  currentTarget.value = null
}

const loginStore = useLoginStore()

const changeExpandStatus = (
  id: number,
  type: 'open' | 'close' | null = null
) => {
  // @ts-expect-error loginStore is js store
  const index = loginStore.chartOfAccountsCollapseId.indexOf(id)

  if (type === 'open') {
    if (index >= 0) loginStore.chartOfAccountsCollapseId.splice(index, 1)
  } else if (type === 'close') {
    if (index < 0) {
      // @ts-expect-error loginStore is js store
      loginStore.chartOfAccountsCollapseId.push(id)
    }
  } else {
    if (index >= 0) loginStore.chartOfAccountsCollapseId.splice(index, 1)
    // @ts-expect-error loginStore is js store
    else loginStore.chartOfAccountsCollapseId.push(id)
  }
}

const expandStatus = computed(() => {
  const newTotalObjStatus =
    // @ts-expect-error loginStore is js store
    props.row.id && loginStore.chartOfAccountsCollapseId.includes(props.row.id)
  return !newTotalObjStatus
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
